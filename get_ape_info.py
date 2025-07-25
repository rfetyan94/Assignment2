from web3 import Web3
from web3.providers.rpc import HTTPProvider
import requests
import json

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)

# You will need the ABI to connect to the contract
# The file 'abi.json' has the ABI for the bored ape contract
# In general, you can get contract ABIs from etherscan
# https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('ape_abi.json', 'r') as f:
    abi = json.load(f)

############################
# Connect to an Ethereum node
ALCHEMY_KEY = "1GJv_NJYS2l-dfBp5iIAn"
api_url = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"
provider = HTTPProvider(api_url)
web3 = Web3(provider)

def get_ape_info(ape_id):
    assert isinstance(ape_id, int), f"{ape_id} is not an int"
    assert 0 <= ape_id, f"{ape_id} must be at least 0"
    assert 9999 >= ape_id, f"{ape_id} must be less than 10,000"

    data = {'owner': "", 'image': "", 'eyes': ""}

    # Set up the contract locally to avoid scope issues
    contract = web3.eth.contract(address=contract_address, abi=abi)

    # Get the owner
    data['owner'] = contract.functions.ownerOf(ape_id).call()

    # Get the tokenURI (which contains metadata including the image)
    token_uri = contract.functions.tokenURI(ape_id).call()

    # If the URI is on IPFS, route it through a gateway
    if token_uri.startswith("ipfs://"):
        token_uri = token_uri.replace("ipfs://", "https://ipfs.io/ipfs/")

    # Download metadata
    metadata = json.loads(requests.get(token_uri).text)

    # Get the image and eyes trait
    data['image'] = metadata.get('image', '')
    for attribute in metadata.get('attributes', []):
        if attribute.get('trait_type') == 'Eyes':
            data['eyes'] = attribute.get('value', '')
            break

    assert isinstance(data, dict), f'get_ape_info{ape_id} should return a dict'
    assert all([a in data.keys() for a in ['owner', 'image', 'eyes']]), "return value should include the keys 'owner','image' and 'eyes'"
    return data
