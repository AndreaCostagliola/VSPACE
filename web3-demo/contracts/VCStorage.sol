// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.0 <0.9.0;

contract VCStore {
    event VCStored(address indexed user, string vc); // Definition of the event
    event MappingAdded(string topic, string cid_db, string cid_acl, string transaction_id); // New event for the mapping

    mapping(address => string) public vcMap;

    struct Mapping {
        string cid_db;
        string cid_acl;
        string transaction_id;
    }

    mapping(string => Mapping[]) public topicMappings;

    function storeVC(string memory vc) public {
        vcMap[msg.sender] = vc;
        emit VCStored(msg.sender, vc); // Emission of the event
    }

    function addMapping(string memory topic, string memory cid_db, string memory cid_acl, string memory txhash) public {
        Mapping memory newMapping = Mapping({
            cid_db: cid_db,
            cid_acl: cid_acl,
            transaction_id: txhash
        });

        topicMappings[topic].push(newMapping);
        emit MappingAdded(topic, cid_db, cid_acl, txhash); // Emission of the event for the mapping
    }

    function getMappings(string memory topic) public view returns (Mapping[] memory) {
        return topicMappings[topic];
    }

    function getMappingByTxHash(string memory topic, string memory txhash) public view returns (string memory cid_db, string memory cid_acl, string memory transaction_id) {
        Mapping[] memory mappings = topicMappings[topic];
        for (uint i = 0; i < mappings.length; i++) {
            if (keccak256(abi.encodePacked(mappings[i].transaction_id)) == keccak256(abi.encodePacked(txhash))) {
                return (mappings[i].cid_db, mappings[i].cid_acl, mappings[i].transaction_id);
            }
        }
        revert("Mapping not found for the provided txhash");
    }
}
