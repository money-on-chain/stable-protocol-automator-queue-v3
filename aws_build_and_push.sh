#!/bin/bash

# exit as soon as an error happen
set -e

usage() { echo "Usage: $0 -e <environment> -c <config file> -i <aws id> -r <aws region>" 1>&2; exit 1; }

while getopts ":e:c:i:r:" o; do
    case "${o}" in
        e)
            e=${OPTARG}
             ((e=="flipago_testnet" || e == "flipago_mainnet" || e == "roc_testnet" || e == "roc_mainnet" )) || usage
            case $e in
                flipago_testnet)
                    ENV=$e
                    ;;
                flipago_mainnet)
                    ENV=$e
                    ;;
                roc_testnet)
                    ENV=$e
                    ;;
                roc_mainnet)
                    ENV=$e
                    ;;
                *)
                    usage
                    ;;
            esac
            ;;
        c)
            c=${OPTARG}
            CONFIG_FILE=$c
            ;;
        i)
            i=${OPTARG}
            AWS_ID=$i
            ;;
        r)
            r=${OPTARG}
            AWS_REGION=$r
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${e}" ] || [ -z "${c}" ] || [ -z "${i}" ] || [ -z "${r}" ]; then
    usage
fi

docker image build -t automator_queue_v2_$ENV -f Dockerfile --build-arg CONFIG=$CONFIG_FILE .

echo "Build done!"

docker tag automator_queue_v2_$ENV:latest $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com/automator_queue_v2_$ENV:latest

docker push $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com/automator_queue_v2_$ENV:latest

echo "Done!"
