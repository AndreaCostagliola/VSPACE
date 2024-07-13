import json
import didkit
from web3 import Web3



class DecentralizedIdentityHelper:


    #constructor
    def __init__(self, config_file_path):
        with open(config_file_path, "r") as file:
            self.config = json.load(file)
            self.ipfs_node_address = self.config["environment_variables"]["IPFS_NODE_ADDRESS"]
            self.ipfs_api_url = self.config["environment_variables"]["IPFS_API_URL"]
            self.http_timeout = self.config["http_settings"].get("timeout", 10)

        self.did = None  # Initialize DID attribute
        
        # Check if DID has been generated before
        if "DID" in self.config:
            self.did = self.config["DID"]
            self.jwk = self.config["JWK"]
        else:
            # Generate ed25519 key and DID only once
            self.jwk = didkit.generate_ed25519_key()
            self.did = didkit.key_to_did("key", self.jwk)
            self.config["JWK"] = self.jwk
            self.config["DID"] = self.did  # Save the DID in the config file
            with open(config_file_path, "w") as file:
                json.dump(self.config, file, indent=4)

    async def verifyVerifiableCredential(self, credential_data):
        try:
            # Assuming credential_data is a dictionary (JSON object), if it's a string, convert it to a dictionary
            if isinstance(credential_data, str):
                credential_data = json.loads(credential_data)

            didkit_options = {
                "proofPurpose": "assertionMethod"
            }

            result = await didkit.verify_credential(json.dumps(credential_data), json.dumps(didkit_options))

            print("The credential has been successfully verified!")
            print("Result:", result)

        except Exception as e:
            print("An error occurred while verifying the credential:", str(e))

    def store_vc(self, vc):
        try:
            
            vc_string = json.dumps(vc) 
            if not vc_string:
                raise ValueError("VC cannot be empty")

            with open(self.contract_path, 'r') as f:
                contract_data = json.load(f)
            contract_abi = contract_data['abi']
            contract_address = contract_data['networks']['1720659142222']['address'] 

 
            web3 = Web3(Web3.HTTPProvider(self.provider_url))

            contract = web3.eth.contract(address=contract_address, abi=contract_abi)


            transaction = contract.functions.storeVC(vc_string).build_transaction({
                'from': self.sender_address,
                'nonce': web3.eth.get_transaction_count(self.sender_address),
                'gas': 2000000,
                'gasPrice': web3.to_wei('1', 'gwei')
            })

     
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            return tx_hash.hex()

        except Exception as e:
            print("An error occurred while storing VC:", str(e))
            return None
        
    def get_vc_from_blockchain(self, hash):
        try:
            with open(self.contract_path, 'r') as f:
                contract_data = json.load(f)
            contract_abi = contract_data['abi']
            contract_address = contract_data['networks']['1720659142222']['address']
            print("contract", contract_address)
            web3 = Web3(Web3.HTTPProvider(self.provider_url))
            if not web3.is_connected():
                print("Error: Not connected to the blockchain")
                return None
            
            contract = web3.eth.contract(address=contract_address, abi=contract_abi)
            receipt = web3.eth.get_transaction_receipt(hash)
        
            if receipt is None:
                print("Error: Transaction receipt not found")
                return None
            events = contract.events.VCStored().process_receipt(web3.eth.get_transaction_receipt(hash))

            if events:
                print(events)
                stored_vc = events[0]['args']['vc']
                return stored_vc
                                        
        except Exception as e:
            print("An error occurred while retrieving vc:", str(e))
        return None
