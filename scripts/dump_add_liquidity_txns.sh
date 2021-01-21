export ALGORAND_DATA=~/node/data
export MANAGER_INDEX="13631691"
export VALIDATOR_INDEX="13631692"
export TOKEN1_INDEX="13631693"
export TOKEN2_INDEX="13631694"
export LIQUIDITY_TOKEN_INDEX="13631695"
export ESCROW_ADDRESS="TWQNZUE3SDL7VQZCEEDKXUGTF2VSTQ6BLJLO5JYXKGANQHARRN46BYWGZ4"
export TEST_ACCOUNT_ADDRESS="7SKGGC2K66FMQVIXH3FVQFSQE6OPPDIACSEHQNZIOEEZULVBICYFEYESGU"

./goal app call --app-id ${VALIDATOR_INDEX} --app-arg "str:a" --app-arg "str:1" --from ${TEST_ACCOUNT_ADDRESS} --foreign-asset ${LIQUIDITY_TOKEN_INDEX} --app-account ${ESCROW_ADDRESS} --app-account ${ESCROW_ADDRESS} --out=txn1.tx

./goal app call --app-id ${MANAGER_INDEX} --app-arg "str:a" --app-arg "str:1" --from ${TEST_ACCOUNT_ADDRESS} --foreign-asset ${LIQUIDITY_TOKEN_INDEX} --app-account ${ESCROW_ADDRESS} --app-account ${ESCROW_ADDRESS} --out=txn2.tx

./goal asset send -a 5 --assetid ${TOKEN1_INDEX} -f ${TEST_ACCOUNT_ADDRESS} -t ${ESCROW_ADDRESS} --out=txn3.tx

./goal asset send -a 5 --assetid ${TOKEN2_INDEX} -f ${TEST_ACCOUNT_ADDRESS} -t ${ESCROW_ADDRESS} --out=txn4.tx

cat txn1.tx txn2.tx txn3.tx txn4.tx > combinedtxns.tx

./goal clerk group -i combinedtxns.tx -o groupedtxns.tx
./goal clerk split -i groupedtxns.tx -o split.tx

./goal clerk sign -i split-0.tx -o signout-0.tx
./goal clerk sign -i split-1.tx -o signout-1.tx
./goal clerk sign -i split-2.tx -o signout-2.tx
./goal clerk sign -i split-3.tx -o signout-3.tx

cat signout-0.tx signout-1.tx signout-2.tx signout-3.tx > signout.tx

./goal clerk dryrun -t signout.tx --dryrun-dump --dryrun-dump-format json -o add_liq_dr.msgp
