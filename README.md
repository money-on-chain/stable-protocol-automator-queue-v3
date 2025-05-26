# Stable Protocol Automator Queue Executor v3 (Multicollateral)

## Warning: This is only for version 3 of the main contracts.

This is a backend queue executor job. Periodic tasks that runs different jobs, 
that call the contracts and asks if they are ready to execute it. This jobs 
run async of the app, and call directly to the contract through node. 

### Currents tasks

 1. Queue Execute. Execute queued operations.
 2. Execute Micro liquidations.
 3. Execute liquidations. 
  
### Usage

**Requirement and installation**
 
*  We need Python 3.10+

Install libraries

`pip install -r requirements.txt`

**Usage**

Select settings from environments/ and copy to ./config.json 

**Run**

`export ACCOUNT_PK_SECRET=(Your PK)`

`python ./app_run_automator.py `

#### Custom node instead using of public node

If you want to use your custom private node pass as environment settings, before running price feeder:

`export APP_CONNECTION_URI=https://public-node.rsk.co`


**Usage Docker**

Build, change path to correct environment

```
docker build -t automator -f Dockerfile --build-arg CONFIG=./enviroments/flipmoney-testnet/config.json .
```

Run, replace ACCOUNT_PK_SECRET  with your private key owner of the account

```
docker run -d \
--name automator_1 \
--env ACCOUNT_PK_SECRET=asdfasdfasdf \
automator
```


### Contracts


**Stable protocol core v2**

*[https://github.com/money-on-chain/stable-protocol-core-v2](https://github.com/money-on-chain/stable-protocol-core-v2)*

**RIF on Chain implementation v2**

*[https://github.com/money-on-chain/stable-protocol-roc-v2](https://github.com/money-on-chain/stable-protocol-roc-v2)*

**Flipmoney implementation v2**

*[https://github.com/money-on-chain/stable-protocol-roc-v2](https://github.com/money-on-chain/stable-protocol-roc-v2)*
