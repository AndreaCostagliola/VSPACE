import json
import didkit


class IssueVerifiableCredential:


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

    # this function issues a verifiable credential and stores it on IPFS
    async def issueVerifiableCredential(self, hash_dt, credential_file_path):
        try:
            # Get verification method for the generated key
            verification_method = await didkit.key_to_verification_method("key", self.jwk)
            with open(credential_file_path, "r") as file:
                credential_data = json.load(file)

            credential_data["issuer"] = self.did
            credential_data["credentialSubject"]["hash"] = hash_dt

            # Sign the credential
            signed_credential = await didkit.issue_credential(
                json.dumps(credential_data),
                json.dumps({}),
                self.jwk)
            return json.loads(signed_credential)

        except Exception as e:
            print("An error occurred while issuing verifiable credential:", str(e))
            return None