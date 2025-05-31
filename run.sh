for i in {23..23}
do
    echo "------------- $i --------------" 
    echo "------------- heuristics_all  --------------" 
    for j in {1..20}
    do
        time gtimeout 1h  python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=$i --heuristics --heuristic_weight=100 --domain_file=./domain/domain_bosch.json  --domain=bosch --num_robots=6
    done
    # echo "------------- heuristics_order  --------------" 
    # for j in {1..10}
    # do
    #     time gtimeout 1h  python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=$i --heuristics_order --heuristic_weight=100 --domain_file=./domain/domain_bosch.json  --domain=bosch --num_robots=2 
    # done
    # echo "------------- heuristics_switch --------------" 
    # for j in {1..10}
    # do
    #     time gtimeout 1h  python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=$i --heuristics_switch --heuristic_weight=100 --domain_file=./domain/domain_bosch.json  --domain=bosch --num_robots=2
    # done
    # echo "------------- heuristics_automaton --------------" 
    # for j in {1..10}
    # do
    #     time gtimeout 1h  python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=$i --heuristics_automaton --heuristic_weight=100 --domain_file=./domain/domain_bosch.json  --domain=bosch --num_robots=2
    # done
    # echo "------------- heuristics_no  --------------" 
    # for j in {1..10}
    # do
    #     time gtimeout 1h  python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=$i --heuristic_weight=100 --domain_file=./domain/domain_bosch.json  --domain=bosch --num_robots=2 
    # done
   
done
# for i in {18..18}
# do
#     echo "------------- $i --------------" 
#     for n in 10
#     do
#         for j in {1..20}
#         do 
#             time gtimeout 30m  python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=$i --heuristics --heuristic_weight=100 --domain_file=./domain/domain_bosch.json  --domain=bosch --num_robots=$n
#         done
#     done
# done