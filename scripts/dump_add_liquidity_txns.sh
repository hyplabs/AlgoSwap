export ALGORAND_DATA=~/node/data

export MANAGER_INDEX="13649731"
export VALIDATOR_INDEX="13649738"
export TOKEN1_INDEX="13649742"
export TOKEN2_INDEX="13649743"
export LIQUIDITY_TOKEN_INDEX="13649749"

export ESCROW_ADDRESS="4SVPQF7DAGYH3W76XECM66UADKWZFJIZKR5JC262FG6RB32KAVEX5AF4RE"
export TEST_ACCOUNT_ADDRESS="LZVKOKRULFYC7TIAOMA76VVPYWUJPRZ6V6FE7ZTMYAL7KNZNKR75HNA3HY"

./goal app call --app-id ${VALIDATOR_INDEX} --app-arg "str:a" --app-arg "str:1" --from ${TEST_ACCOUNT_ADDRESS} --foreign-asset ${LIQUIDITY_TOKEN_INDEX} --app-account ${ESCROW_ADDRESS} --app-account ${ESCROW_ADDRESS} --out=txn1.tx

./goal app call --app-id ${MANAGER_INDEX} --app-arg "str:a" --app-arg "str:1" --from ${TEST_ACCOUNT_ADDRESS} --foreign-asset ${LIQUIDITY_TOKEN_INDEX} --app-account ${ESCROW_ADDRESS} --app-account ${ESCROW_ADDRESS} --out=txn2.tx

./goal asset send -a 500000 --assetid ${TOKEN1_INDEX} -f ${TEST_ACCOUNT_ADDRESS} -t ${ESCROW_ADDRESS} --out=txn3.tx

./goal asset send -a 500000 --assetid ${TOKEN2_INDEX} -f ${TEST_ACCOUNT_ADDRESS} -t ${ESCROW_ADDRESS} --out=txn4.tx

cat txn1.tx txn2.tx txn3.tx txn4.tx > combinedtxns.tx

./goal clerk group -i combinedtxns.tx -o groupedtxns.tx
./goal clerk split -i groupedtxns.tx -o split.tx

./goal clerk sign -i split-0.tx -o signout-0.tx
./goal clerk sign -i split-1.tx -o signout-1.tx
./goal clerk sign -i split-2.tx -o signout-2.tx
./goal clerk sign -i split-3.tx -o signout-3.tx

cat signout-0.tx signout-1.tx signout-2.tx signout-3.tx > signout.tx

./goal clerk dryrun -t signout.tx --dryrun-dump --dryrun-dump-format json -o add-liq-dr.json
