import csv
import json
import didkit
import requests
from web3 import Web3



class DataRetrievalHelper:


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
        
    def get_mapping_by_topic(self, topic):
        try:
            with open(self.contract_path, 'r') as f:
                contract_data = json.load(f)
            contract_abi = contract_data['abi']
            contract_address = contract_data['networks']['1720659142222']['address']

            web3 = Web3(Web3.HTTPProvider(self.provider_url))
            if not web3.is_connected():
                return None

            contract = web3.eth.contract(address=contract_address, abi=contract_abi)

            mapping = contract.functions.getMappings(topic).call()
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
        
    def getfromIPFS(self, cid):
        try:
            url = self.ipfs_api_url
            params = {'arg': cid}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                filename = f'{cid}.csv'
                with open(filename, 'wb') as file:
                    file.write(response.content)
                    print("The file has been downloaded successfully.")
                return filename
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print("An error occurred while fetching file from IPFS:", str(e))
            return None
    
    def search_did_in_csv(self, csv_file, did_to_find):
        with open(csv_file, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if self.find_did_in_rows(row, did_to_find):
                    return True
        return False

    def find_did_in_rows(self, row, did_to_find):
        for sublist in row:
            if isinstance(sublist, list):
                for item in sublist:
                    if isinstance(item, str) and did_to_find in item:
                        return True
            elif isinstance(sublist, str) and did_to_find in sublist:
                return True
        return False
    
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
    
    


