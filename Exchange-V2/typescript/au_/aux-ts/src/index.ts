// module exports
import {AuxEnv, getAptosProfile} from "./env";

export * as client from "./client";
export * as clob from "./clob";
export * as units from "./units";
export * as vault from "./vault";
export * as router from "./router";
export { Account, Market, MarketSubscriber, Router, Vault };
export { AU, DU };

// type exports
import Account from "./account";
import Market from "./clob/dsl/market";
import Router from "./router/dsl/router";
import MarketSubscriber from "./subscriber";
import {AU, DU, Pct} from "./units";
import Vault from "./vault/dsl/vault";
import {AuxClient} from "./client";
import {AptosAccount} from "aptos";
import {ConstantProductClient} from "./pool/constant-product/client";
import {Command} from "commander";

async function Swap(
  Amount: number,
  side: string,
  coinTypeLeft: string,
  coinTypeRight: string,
){
  console.log('pt1: ' + Date.parse(new Date().toString()))
  const coinType0 = coinTypeLeft
  const coinType1 = coinTypeRight
  const aptosProfile = getAptosProfile("default")
  const auxEnv = new AuxEnv("mainnet", aptosProfile);
  const auxClient = new AuxClient(auxEnv.aptosNetwork, auxEnv.aptosClient);
  auxClient.sender = AptosAccount.fromAptosAccountObject({privateKeyHex: <string>aptosProfile.private_key})

  console.log('pt2: ' + Date.parse(new Date().toString()))
  // console.log("swapping...")
  if(side == "SELL") {
    const poolClient = new ConstantProductClient(auxClient, {
      coinTypeX: coinType0,
      coinTypeY: coinType1
    });
    // console.log(">>>> Swapping from APT to USDC == SELL")
    await poolClient.swap(
      {
        coinTypeIn: coinType0,
        exactAmountIn: DU(Amount),
        parameters: {
          slippage: new Pct(10)
        },
      }
    )
    console.log('pt3: ' + Date.parse(new Date().toString()))
    // console.log(tx.transaction.hash)
  }else if(side == "BUY"){
    const poolClient = new ConstantProductClient(auxClient, {
      coinTypeX: coinType0,
      coinTypeY: coinType1
    });
    // console.log(">>>> Swapping from APT to USDC == SELL")
    await poolClient.swap(
      {
        coinTypeOut: coinType0,
        exactAmountOut: DU(Amount),
        parameters: {
          slippage: new Pct(10)
        },
      }
    )
    console.log('pt3: ' + Date.parse(new Date().toString()))
    // console.log(tx.transaction.hash)
  }else{
    // console.log("parameter {side} is error")
  }
  console.log('pt4: ' + Date.parse(new Date().toString()))
}

const program = new Command();

program
  .command("swap")
  .argument('<sellAmount>')
  .argument('<side>')
  .argument('<coinTypeLeft>')
  .argument('<coinTypeRight>')
  .action(Swap)

program.parse();
// Swap(
//   1,
//   "BUY", // "SELL"
//   "0x1::aptos_coin::AptosCoin",
//   "0x5e156f1207d0ebfa19a9eeff00d62a282278fb8719f4fab3a586a0a2c0fffbea::coin::T"
// )