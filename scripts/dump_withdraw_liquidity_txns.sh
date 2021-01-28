export ALGORAND_DATA=~/node/data

export ESCROW_ADDRESS="GE25LQU674ZQFAYJM2RUCRXQRPWIMAEOUI26NHRDW77GEHRANYSRUTQYFE"
export ESCROW_LOGICSIG="AiALAQMEBqqAygangMoGAozr3AWrgMoGrIDKBq2AygYyBCISQAB6MgQjEkAAQDIEJBJAAAEAMwAQJRIzABghBBIQMwEQJRIQMwEYIQUSEDEWIQYSMRYjEhEQMRAkEhAxCTIDEhAxFTIDEhBCAGwzABAlEjMAGCEEEhAzARAlEhAzARghBRIQMRYhBhIQMRAkEhAxCTIDEhAxFTIDEhBCADkxGSISMQQhBw4QMRghBBIxGCEFEhEQMRAkEjEAMRQSEDEEIQcOEDERIQgSMREhCRIRMREhChIREBE="

export MANAGER_INDEX="13795367"
export VALIDATOR_INDEX="13795370"
export TOKEN1_INDEX="13795371"
export TOKEN2_INDEX="13795372"
export LIQUIDITY_TOKEN_INDEX="13795373"
export TEST_ACCOUNT_ADDRESS="LZVKOKRULFYC7TIAOMA76VVPYWUJPRZ6V6FE7ZTMYAL7KNZNKR75HNA3HY"

./goal app call --app-id ${VALIDATOR_INDEX} --app-arg "str:w" --app-arg "str:1" --app-arg "str:1" --from ${TEST_ACCOUNT_ADDRESS} --app-account ${ESCROW_ADDRESS} --out=txn1.tx

./goal app call --app-id ${MANAGER_INDEX} --app-arg "str:w" --app-arg "str:1" --app-arg "str:1" --from ${TEST_ACCOUNT_ADDRESS} --app-account ${ESCROW_ADDRESS} --out=txn2.tx

./goal asset send -a 500000000 --assetid ${LIQUIDITY_TOKEN_INDEX} -f ${TEST_ACCOUNT_ADDRESS} -t ${ESCROW_ADDRESS} --out=txn3.tx

cat txn1.tx txn2.tx txn3.tx > combinedtxns.tx

./goal clerk group -i combinedtxns.tx -o groupedtxns.tx
./goal clerk split -i groupedtxns.tx -o split.tx

./goal clerk sign -i split-0.tx -o signout-0.tx
./goal clerk sign -i split-1.tx -o signout-1.tx
./goal clerk sign -i split-2.tx -o signout-2.tx

cat signout-0.tx signout-1.tx signout-2.tx > signout.tx

./goal clerk dryrun -t signout.tx --dryrun-dump --dryrun-dump-format json -o withdraw-liq-dr.json