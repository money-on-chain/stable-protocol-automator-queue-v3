# Stable Protocol Automator Queue Executor v3 (Multicollateral)

## Warning: This is only for version 3 of the main contracts.

This is a backend queue executor job. Periodic tasks that runs different jobs, 
that call the contracts and asks if they are ready to execute it. This jobs 
run async of the app, and call directly to the contract through node. 

### Currents tasks

 1. Queue Execute. Execute queued operations.
 2. Execute Micro liquidations.
 3. Execute liquidations. 

Optional settings:

`max_fee_per_gas` and `max_priority_fee_per_gas` can be set at the top level of the config to send EIP-1559 style transactions.
  
### Usage

**Requirements and installation**

* Python 3.10+

```bash
pip install -r requirements.txt
```

**Configuration**

Select a settings file from `environments/` and copy it to `./config.json`.

**Environment variables**

Create a `.env` file from the provided example — never commit it to version control:

```bash
cp .env.example .env
```

Then edit `.env` and set your values:

```ini
# Required: private key of the signing account
ACCOUNT_PK_SECRET=your_private_key_here

# Optional: override the RPC node from config.json
# APP_CONNECTION_URI=https://public-node.rsk.co
```

The app loads `.env` automatically on startup. No `export` or `source` needed.

| Variable | Required | Description |
|---|---|---|
| `ACCOUNT_PK_SECRET` | Yes | Private key of the signing account. Accepts a single key or a comma-separated list (`pk1,pk2,pk3`). |
| `ACCOUNT_PK_SECRET_1` … `_9` | No | Additional signing accounts via numbered variables. |
| `APP_CONNECTION_URI` | No | RPC endpoint — overrides `uri` in `config.json`. |
| `APP_CONFIG` | No | Full config as a JSON string — replaces `config.json` entirely. |

**Run**

```bash
python ./app_run_automator.py
```

**Usage Docker**

Build — change the path to the correct environment config:

```bash
docker build -t automator -f Dockerfile --build-arg CONFIG=./environments/flipmoney-testnet/config.json .
```

Run — pass secrets via `--env-file` so they never appear in shell history or `docker inspect`:

```bash
docker run -d \
  --name automator_1 \
  --env-file .env \
  automator
```


### Contracts


**Stable protocol core v2**

*[https://github.com/money-on-chain/stable-protocol-core-v2](https://github.com/money-on-chain/stable-protocol-core-v2)*

**RIF on Chain implementation v2**

*[https://github.com/money-on-chain/stable-protocol-roc-v2](https://github.com/money-on-chain/stable-protocol-roc-v2)*

**Flipmoney implementation v2**

*[https://github.com/money-on-chain/stable-protocol-roc-v2](https://github.com/money-on-chain/stable-protocol-roc-v2)*
