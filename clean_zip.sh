#!/bin/bash


dir=$(cd $(dirname $0);pwd)
cd $dir

size=`du -s .|awk '{print $1}'`

maxSize=$1

declare -a fileList

listZip(){
    zipList=`ls -al -rt *.zip | awk '{print $9}'`
    i=0
    for file in $zipList 
    do
       fileList[$i]=$file
       i=`expr $i + 1` 
    done
    # the easy way
    #fileList=(zipList)
}


cleanZip(){
    len=${#fileList[*]}
    if [ $size -gt $maxSize ]; then
        for zip in $(seq 0 `expr $len - 2`)
        do
            rm -rf  ${fileList[$zip]}
            echo ${fileList[$zip]} > ./clean_log
        done
    fi
}


listZip
cleanZip
