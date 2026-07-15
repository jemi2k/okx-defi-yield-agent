"""
Pytest configuration
"""
import sys

# Block the broken web3.pytest_ethereum plugin from loading
# This module has an import error (ContractName from eth_typing)
BROKEN_WEB3_MODULES = [
    "web3.tools",
    "web3.tools.pytest_ethereum",
    "web3.tools.pytest_ethereum.deployer",
]
for mod_name in BROKEN_WEB3_MODULES:
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    sys.modules[mod_name] = type(sys)("dummy_module")