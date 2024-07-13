var VCStore = artifacts.require("./VCStore");

module.exports = function(deployer) {
  deployer.deploy(VCStore);
};