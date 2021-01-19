export VALIDATOR_INDEX="13605355"
export MANAGER_INDEX="13605356"
export TOKEN1_INDEX=""
export TOKEN2_INDEX=""
export LIQUIDITY_TOKEN_INDEX=""
export ESCROW_ADDRESS=""
export TEST_ACCOUNT_ADDRESS=""

./goal app call --app-id ${VALIDATOR_INDEX} --app-arg "str:a" --app-arg "str:5" --from ${TEST_ACCOUNT_ADDRESS} --app-account ${ESCROW_ADDRESS} --app-account ${ESCROW_ADDRESS} --foreign-asset ${LIQUIDITY_TOKEN_INDEX} --out=txn1.tx

./goal app call --app-id ${MANAGER_INDEX} --app-arg "str:a" --app-arg "str:5" --from ${TEST_ACCOUNT_ADDRESS} --app-account ${ESCROW_ADDRESS} --app-account ${ESCROW_ADDRESS} --foreign-asset ${LIQUIDITY_TOKEN_INDEX} --out=txn2.tx

./goal asset send -a 50 --assetid ${TOKEN1_INDEX} -f ${TEST_ACCOUNT_ADDRESS} -t ${ESCROW_ADDRESS} --out=txn3.tx

./goal asset send -a 50 --assetid ${TOKEN2_INDEX} -f ${TEST_ACCOUNT_ADDRESS} -t ${ESCROW_ADDRESS} --out=txn4.tx

cat txn1.tx txn2.tx txn3.tx txn4.tx > combinedtxns.tx

./goal clerk group -i combinedtxns.tx -o groupedtxns.tx
./goal clerk split -i groupedtxns.tx -o split.tx

./goal clerk sign -i split-0.tx -o signout-0.tx
./goal clerk sign -i split-1.tx -o signout-1.tx
./goal clerk sign -i split-2.tx -o signout-2.tx
./goal clerk sign -i split-3.tx -o signout-3.tx

cat signout-0.tx signout-1.tx signout-2.tx signout-3.tx > signout.tx

./goal clerk dryrun -t signout.tx --dryrun-dump -o add_liq_dr.msgp
