# for i in {12..14}
# do
#     echo "------------- $i --------------" 
#     for j in {1..20}
#     do
#         time gtimeout 1h  python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=$i --heuristic_weight=0 --domain_file=/Users/xushengluo/Documents/Code/Hierarchical-LTL-STAP/src/domain_bosch.json  --domain=bosch
#     done
# done

for i in {18..18}
do
    echo "------------- $i --------------" 
    for n in 10
    do
        for j in {1..20}
        do 
            time gtimeout 30m  python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=$i --heuristics --heuristic_weight=100 --domain_file=/Users/xushengluo/Documents/Code/Hierarchical-LTL-STAP/src/domain_bosch.json  --domain=bosch --num_robots=$n
        done
    done
done