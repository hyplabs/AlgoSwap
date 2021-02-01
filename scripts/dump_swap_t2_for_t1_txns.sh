export ALGORAND_DATA=~/node/data

export ESCROW_ADDRESS="C3BOJXVCV2NIJELWL7P3MW6FE6X6W6QKJSCNM5DKNTQ7Y7IMAPOBMLXD4U"
export ESCROW_LOGICSIG="AiALAQMEBq3V1Qaq1dUGAsLZ4QWw1dUGsdXVBrLV1QYyBCISQAB6MgQjEkAAQDIEJBJAAAEAMwAQJRIzABghBBIQMwEQJRIQMwEYIQUSEDEWIQYSMRYjEhEQMRAkEhAxCTIDEhAxFTIDEhBCAGwzABAlEjMAGCEEEhAzARAlEhAzARghBRIQMRYhBhIQMRAkEhAxCTIDEhAxFTIDEhBCADkxGSISMQQhBw4QMRghBBIxGCEFEhEQMRAkEjEAMRQSEDEEIQcOEDERIQgSMREhCRIRMREhChIREBE="

export MANAGER_INDEX="13986474"
export VALIDATOR_INDEX="13986477"
export TOKEN1_INDEX="13986480"
export TOKEN2_INDEX="13986481"
export LIQUIDITY_TOKEN_INDEX="13986482"
export TEST_ACCOUNT_ADDRESS="SI36B6M4HKFJFRODQ4V3P726E56DVPMAF4A3HW5IIEA7IDDIW4IEPSE2UU"

./goal app call --app-id ${VALIDATOR_INDEX} --app-arg "str:s2" --app-arg "int:8088850" --from ${TEST_ACCOUNT_ADDRESS} --app-account ${ESCROW_ADDRESS} --out=txn1.tx

./goal app call --app-id ${MANAGER_INDEX} --app-arg "str:s2" --app-arg "int:8088850" --from ${TEST_ACCOUNT_ADDRESS} --app-account ${ESCROW_ADDRESS} --out=txn2.tx

./goal asset send -a 10000000 --assetid ${TOKEN1_INDEX} -f ${TEST_ACCOUNT_ADDRESS} -t ${ESCROW_ADDRESS} --out=txn3.tx

cat txn1.tx txn2.tx txn3.tx > combinedtxns.tx

./goal clerk group -i combinedtxns.tx -o groupedtxns.tx
./goal clerk split -i groupedtxns.tx -o split.tx

./goal clerk sign -i split-0.tx -o signout-0.tx
./goal clerk sign -i split-1.tx -o signout-1.tx
./goal clerk sign -i split-2.tx -o signout-2.tx

cat signout-0.tx signout-1.tx signout-2.tx > signout.tx

./goal clerk dryrun -t signout.tx --dryrun-dump --dryrun-dump-format json -o swap-t2-for-t1-dr.json