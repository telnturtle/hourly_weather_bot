#!/bin/bash

today=$(date +"%FT%H-%M-%S")
filename="_log/$today.log"

python3 -u $1 > $filename 2> $filename &
