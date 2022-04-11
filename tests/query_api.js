const axios = require('axios');
const Web3 = require('web3');

async function getSignature(message) {
  let req = await axios.post('https://XXX.amazonaws.com/prod/items/', 
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
  var web3 = new Web3(new Web3.providers.HttpProvider('https://localhost:8545'))
  
  let message = 'hello'
  let message_hash = await web3.eth.accounts.hashMessage(message)
  console.log(message_hash)
  
  let res = await getSignature(message)
  console.log(res)

  let r = res.r
  console.log(r + " : " + typeof(r))
  let s = res.s
  console.log(s + " : " + typeof(s))

  let recovered_addr_1 = web3.eth.accounts.recover(message_hash, '0x1c', r, s, true);
  console.log(recovered_addr_1)

  let recovered_addr_2 = web3.eth.accounts.recover(message_hash, '0x1d', r, s, true);
  console.log(recovered_addr_2)

}

test()
