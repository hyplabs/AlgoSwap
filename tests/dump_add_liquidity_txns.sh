export VALIDATOR_INDEX="13616699"
export MANAGER_INDEX="13616702"
export TOKEN1_INDEX="13616706"
export TOKEN2_INDEX="13616707"
export LIQUIDITY_TOKEN_INDEX="13616714"
export ESCROW_ADDRESS="AUNTAWAYVOG2WTNKVMTM7XTTZRJYPUYESH3GZT4B23YMPY6CNB55KWHLUM"
export TEST_ACCOUNT_ADDRESS="EFU57I3AX2473QAKM2E4QS7KEMAXOISYY62PE36RKNDJ7RR4X2JJDUFZAQ"

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

./goal clerk dryrun -t signout.tx --dryrun-dump --dryrun-dump-format json -o add_liq_dr.msgp
