#!/bin/sh
job=Job62526_output_catra_baseline
for logdir in ${job}/Catra/Catra\ 0.1.5___def/*.par
do
    instance=../deduped-benchmarks/$(basename "$logdir")
    if  grep --quiet "===" "$logdir"/*.txt;
    then
        grep "===" "$logdir"/*.txt \
            | sd --fixed-strings "../../benchmark/theBenchmark.par" "${instance}" \
            | sd "^.*\t" ""
    else
        # Fake a timeouot log
        echo "==== ${instance}: timeout > 30000ms run: 30.1s parse: 0.1s ===="
    fi

    #popd
done
