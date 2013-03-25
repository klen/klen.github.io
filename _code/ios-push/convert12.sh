#!/bin/bash

convert () {
    FILENAME=$1
    BASENAME=${FILENAME%.*}
    EXT=${FILENAME#*.}

    case "$EXT" in
        p12)
            echo "Convert $FILENAME to $BASENAME.pem"
            openssl pkcs12 -in $FILENAME -out $BASENAME.pem -nodes -clcerts && echo "done - $BASENAME.pem"
        ;;
        *)
            echo "Unknown format: '$EXT'" >&2
		exit 1
		;;
    esac
}

test () {
    MODE=${1:-dev}
    CERTNAME=$2
    
    if [ "$MODE" = "dev" ]; then
        echo $CERTNAME
        openssl s_client -connect gateway.sandbox.push.apple.com:2195 -cert $CERTNAME -key $CERTNAME
    else
        echo $CERTNAME
        openssl s_client -connect gateway.push.apple.com:2195 -cert $CERTNAME -key $CERTNAME
    fi
}

case "$1" in
    convert)
        convert $2
    ;;

    test)
        test $3 $2
    ;;

	*)
		echo "Usage: {convert|test} FILENAME [MODE]" >&2
		exit 1
		;;
esac

exit 0
