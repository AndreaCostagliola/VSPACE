import hashlib

class hashlHelper:

    def hash_file(self, file_path, algorithm='sha256'):
            try:
                # Creiamo un oggetto hash basato sull'algoritmo specificato
                hasher = hashlib.new(algorithm)
                
                # Apriamo il file in modalità binaria
                with open(file_path, 'rb') as f:
                    # Leggiamo il file in blocchi per evitare di caricare tutto il file in memoria
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)
                
                # Restituiamo l'hash in formato esadecimale
                return hasher.hexdigest()
            
            except Exception as e:
                print(f"An error occurred while hashing the file: {e}")
                return None