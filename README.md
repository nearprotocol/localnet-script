# Script to run several near nodes locally

1. Get near binary. Usually clone [nearcore](https://github.com/nearprotocol/nearcore) and compile it using `cargo build -p near --release`.

2. Modify `config.ini` to point to your binary.

3. Start with `python3 start_localnet.py`

## Stop

To stop the network run `python3 start_localnet.py -k`