import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'query'))
from translate import translate_en_to_kn

test_text = "2. Cheating (Multiple FIRs) - ************"
print("English:", test_text)
print("Kannada:", translate_en_to_kn(test_text))
