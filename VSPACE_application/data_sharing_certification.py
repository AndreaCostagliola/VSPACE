import csv
import json
import didkit
import requests
from web3 import Web3



class DataSharingCertificationHelper:


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

    def saveDatasetToIPFS(self, dataset_file_path):
            try:
                file_name = dataset_file_path.split("/")[-1]
                # Read content of CSV dataset file
                with open(dataset_file_path, "r") as file:
                    dataset_content = file.read()

                # Add dataset to IPFS node cluster
                files = {'file': (file_name, dataset_content)}
                response = requests.post(self.ipfs_node_address + "/add", files=files)
                return response.json()

            except Exception as e:
                print("An error occurred while saving dataset to IPFS:", str(e))
                return None
      
    def saveACL(self, acl_file_path):
        try:
            file_name = acl_file_path.split("/")[-1]
            with open(acl_file_path, "r") as file:
                acl_content = file.read()
            files = {'file': (file_name, acl_content)}
            response = requests.post(self.ipfs_node_address + "/add", files=files)
            return response.json()

        except Exception as e:
            print("An error occurred while saving ACL to IPFS:", str(e))
            return None
        
    def extract_cid(self, data):
        try:
            cid_value = data['cid']
            return cid_value
        except KeyError as e:
            print("Key 'cid' not found in the dictionary:", str(e))
            return None
        except Exception as e:
            print("An error occurred while extracting CID:", str(e))
            return None
        
    def extract_topic(self,credential_path):
        with open(credential_path, 'r') as vc_file:
            vc = json.load(vc_file)
        types = vc.get("type", [])
        if isinstance(types, list) and len(types) > 1:
            return types[1]
        return None
    
    def add_mapping(self, topic, cid_db, cid_acl, txhash):
        try:
            with open(self.contract_path, 'r') as f:
                contract_data = json.load(f)
            contract_abi = contract_data['abi']
            contract_address = contract_data['networks']['1720659142222']['address']

            web3 = Web3(Web3.HTTPProvider(self.provider_url))

            contract = web3.eth.contract(address=contract_address, abi=contract_abi)

            transaction = contract.functions.addMapping(topic, cid_db, cid_acl, txhash).build_transaction({
                'from': self.sender_address,
                'nonce': web3.eth.get_transaction_count(self.sender_address),
                'gas': 2000000,
                'gasPrice': web3.to_wei('1', 'gwei')
            })

            signed_txn = web3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()

        except Exception as e:
            print("An error occurred while adding mapping:", str(e))
            return None
        
    def get_mapping_by_txhash(self, topic, txhash):
        try:
            with open(self.contract_path, 'r') as f:
                contract_data = json.load(f)
            contract_abi = contract_data['abi']
            contract_address = contract_data['networks']['1720659142222']['address']

            web3 = Web3(Web3.HTTPProvider(self.provider_url))
            if not web3.is_connected():
                return None

            contract = web3.eth.contract(address=contract_address, abi=contract_abi)

            mapping = contract.functions.getMappingByTxHash(topic, txhash).call()
            cid_db, cid_acl, transaction_id = mapping

            return {
                "topic": topic,
                "cid_db": cid_db,
                "cid_acl": cid_acl,
                "transaction_id": transaction_id
            }

        except Exception as e:
            print("An error occurred while retrieving mapping:", str(e))
            return None
