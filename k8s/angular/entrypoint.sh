#!/bin/sh
OK="\t[\e[92m✓\e[0m]"
KO="\t[\e[91m✗\e[0m]"

if [ ! -z $GIT_REPO ]
then
    echo -n `date +"%F %X"` Cloning

    if [ $QUIET='True' ]
        then
            cd /app && git clone --quiet https://"$GIT_USER":"$GIT_TOKEN"@github.com/"$GIT_REPO".git . >/dev/null 2>&1
        else
            cd /app && git clone --quiet https://"$GIT_USER":"$GIT_TOKEN"@github.com/"$GIT_REPO".git .
    fi

    if [ $? -eq 0 ]
    then
        echo -e $OK
    else
        echo -e $KO
    fi
else
        echo `date +"%F %X"` "Cloning not performed (GIT_REPO missing)"
fi

echo -n `date +"%F %X"` Updating
if [ $QUIET='True' ]
    then
        npm update --silent >/dev/null 2>&1
    else
        npm update
fi
if [ $? -eq 0 ]
then
    echo -e $OK
else
    echo -e $KO
fi

if [ -d $OUTPUT_PATH ]
then
    echo -n `date +"%F %X"` Building

    if [ $QUIET='True' ]
    then
        cd /app && ng build --prod --outputPath=$OUTPUT_PATH >/dev/null 2>&1
    else
        cd /app && ng build --prod --outputPath=$OUTPUT_PATH
    fi

    if [ $? -eq 0 ]
    then
        echo -e $OK
    else
        echo -e $KO
    fi
else
    echo `date +"%F %X"` "Building not performed (OUTPUT_PATH not found)"
fi
echo `date +"%F %X"` "We're done"
