# Entrypoint for evaluating papers using LLMs

import sys
from evaluate_papers.main import main

if __name__ == "__main__":
    sys.exit(main())
