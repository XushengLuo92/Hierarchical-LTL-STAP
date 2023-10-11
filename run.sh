for i in {21..21}
do
    echo "------------- $i --------------" 
    for j in {1..20}
    do
        time gtimeout 10m  python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=$i --heuristic_weight=100 --domain_file=/Users/xushengluo/Documents/Code/Hierarchical-LTL-STAP/src/domain_bosch.json  --domain=bosch
    done
done

