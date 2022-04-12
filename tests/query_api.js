const axios = require('axios');
const Web3 = require('web3');

async function getSignature(message, url) {
  let req = await axios.post(url, 
    {
      "operation": "sign_message", 
      "message": message
    })
  try{
    return req.data
  } catch (error) {
    console.error(error)
  }
}

async function test(){
  let args = process.argv

  let message = args[2]
  console.log("\n" + "Message to be signed: '" + message + "' \n")

  let url = args[3]
  console.log("API url: " + url + "\n")

  var web3 = new Web3(new Web3.providers.HttpProvider('https://localhost:8545'))
  
  let message_hash = await web3.eth.accounts.hashMessage(message)

  let res = await getSignature(message, url)
  
  console.log("API response:")
  console.log(res)
  console.log(" ")

  let r = res.r
  let s = res.s

  // Determine two address possibilities:

  console.log("Possible addresses:")

  let recovered_addr_1 = web3.eth.accounts.recover(message_hash, '0x1c', r, s, true);
  console.log("checksum address for v = 27: " + recovered_addr_1)

  let recovered_addr_2 = web3.eth.accounts.recover(message_hash, '0x1d', r, s, true);
  console.log("checksum address for v = 28: " + recovered_addr_2)
  console.log(" ")
}

test()
