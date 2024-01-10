# Simultaneous Task Allocation and Planning for Multi-Robots under Hierarchical Temporal Logic Specifications
Past research into robotic planning with temporal logic specifications, notably Linear Temporal Logic (LTL), was largely based on singular formulas for individual or groups of robots. But with increasing task complexity, LTL formulas unavoidably grow lengthy, complicating interpretation and spec- ification generation, and straining the computational capacities of the planners. We capitalized on the intrinsic structure of tasks and introduced a hierarchical structure to LTL specifi- cations, which have proven to be more expressive than their flat counterparts. We also designed an algorithm to ascertain whether they are satisfied given an input sequence. Second, we employ a search-based approach to synthesize plans for a multi-robot system, accomplishing simultaneous task allocation and planning. The search space is approximated by loosely interconnected sub-spaces, with each sub-space corresponding to one LTL specification. The search is predominantly confined to a single sub-space, transitioning to another sub-space under certain conditions, determined by the decomposition of automatons. Moreover, multiple heuristics are formulated to expedite the search significantly. A theoretical analysis concerning complete- ness and optimality is conducted under mild assumptions. When compared with existing methods on service tasks, our method outperforms in terms of execution times with comparable solution quality. Finally, scalability is evaluated by testing a group of 30 robots and achieving reasonable runtimes.

# Install
 The code is tesed using Python 3.10.12.
### Develop via Conda
 Following the instruction:
```bash
cd /path/to/Hierarchical-LTL-Stap
conda env create -f environment.yml
```
### Import as package
```bash
cd /path/to/Hierarchical-LTL-Stap
pip install -e .
```
### Install ltl2ba
Download the software `LTL2BA` from this [link](http://www.lsv.fr/~gastin/ltl2ba/index.php), and follow the instructions to generate the exectuable `ltl2ba` and then copy it into the folder `Hierarchical-LTL-Stap`, same hierarchy level with `hierarchical_LTL_stap_on_the_fly.py`.
# Example
### Environment 
![](data/bosch.png)
The office building is depicted using a grid-based layout, where areas $d_1$ to $d_{14}$ represent desks, $m_1$ to $m_6$ are meeting rooms, $e$ stands for the elevator, $g$ for the garbage room, $p$ for the printer room, and $k$ for the coffee kitchen. Areas marked as "public" indicate public spaces. Obstacles are illustrated in gray. The locations of robots are shown as numbered red dots.
### Scenario 1 
Empty a paper bin located at desk $d_5$. During this task, the robot must avoid the public area while transporting the bin.
$$
\begin{align*}
 L_1: \quad &  \phi(1,1) =  \Diamond \phi(2,1) \wedge \Diamond\phi(2,2)\\
 L_2: \quad &  \phi(2,1) = \Diamond (d_5 \wedge \mathsf{default} \\ 
 &\quad \quad \quad \quad \wedge \bigcirc ((\mathsf{carrybin}\; \mathcal{U}\; \mathsf{dispose}) \wedge \Diamond \mathsf{default}))  \\ 
 & \quad \quad \quad \quad \wedge \square (\mathsf{carrybin \Rightarrow \neg \mathsf{public}})\\
                & \phi(2,2) = \Diamond (d_5 \wedge \mathsf{emptybin} \wedge \bigcirc (d_5 \wedge \mathsf{default})) 
\end{align*}
$$

```bash
python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=12 --heuristics --heuristic_weight=100 --domain_file=./domain/domain_bosch.json  --domain=bosch --num_robots=6 --vis --print_step 
```
The explanation of arguments can be found in function [create_parser](hierarchical_ltl_stap/util.py).
### Scenario 2
Distribute printed copies of a document to desks $d_{10}$, $d_7$, and $d_5$, and avoid public areas while carrying the document. 
$$
\begin{align*}
L_1: \quad &  \phi(1,1) =  \Diamond\phi(2,1) \wedge \Diamond\phi(2,2) \wedge \Diamond\phi(2,3)\\
 L_2: \quad &  \phi(2,1) = \Diamond (p \wedge \mathsf{carry}\; \mathcal{U}\; (d_{10} \wedge \bigcirc \neg \mathsf{carry})) \\ 
 &\quad \quad \quad \quad \wedge \square (\mathsf{carry} \Rightarrow \neg \mathsf{public})  \\
 &  \phi(2,2) = \Diamond (p \wedge \mathsf{carry}\; \mathcal{U}\; (d_{7} \wedge \bigcirc \neg \mathsf{carry})) \\ 
 &\quad \quad \quad \quad \wedge \square (\mathsf{carry} \Rightarrow \neg \mathsf{public})  \\
 &  \phi(2,3) = \Diamond (p \wedge \mathsf{carry}\; \mathcal{U}\; (d_{5} \wedge \bigcirc \neg \mathsf{carry})) \\ 
 &\quad \quad \quad \quad \wedge \square (\mathsf{carry} \Rightarrow \neg \mathsf{public})  
\end{align*}
$$
```bash
python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=13 --heuristics --heuristic_weight=100 --domain_file=./domain/domain_bosch.json  --domain=bosch --num_robots=6 --vis --print_step 
```
### Scenario 3
Take a photo in meeting rooms $m_1$, $m_4$, and $m_6$. The camera should be turned off for privacy reasons when not in meeting rooms. Deliver a document from desk $d_5$ to $d_3$, ensuring it does not pass through any public areas, as the document is internal and confidential. Guide a person waiting at desk $d_{11}$ to meeting room $m_6$.

$$
\begin{align*}
 L_1: \quad &  \phi(1,1) =  \Diamond\phi(2,1) \wedge \Diamond \phi(2,2) \wedge  \Diamond \phi(2,3)\\
 L_2: \quad &  \phi(2,1) = \Diamond \phi(3,1)\wedge \Diamond \phi(3,2)\wedge \Diamond \phi(3,3)\\
  &  \phi(2,2) = \Diamond (d_5 \wedge \mathsf{carry} \; \mathcal{U} \; (d_3 \wedge \bigcirc \neg \mathsf{carry})) \\
  & \quad \quad \quad \quad \wedge \square (\mathsf{carry} \Rightarrow \neg \mathsf{public}) \\
  &  \phi(2,3) = \Diamond (d_{11}\wedge \mathsf{guide} \; \mathcal{U}\; (m_6 \wedge \bigcirc \neg \mathsf{guide})) \\
 L_3: \quad &  \phi(3,1) = \Diamond(m_1 \wedge \mathsf{photo}) \wedge \square (\neg \mathsf{meeting} \Rightarrow \neg \mathsf{camera} ) \\
 &  \phi(3,2) = \Diamond(m_4 \wedge \mathsf{photo})\wedge \square (\neg \mathsf{meeting} \Rightarrow \neg \mathsf{camera} ) \\
 &  \phi(3,3) = \Diamond(m_6 \wedge \mathsf{photo}) \wedge \square (\neg \mathsf{meeting} \Rightarrow \neg \mathsf{camera} ) \\
 & \mathsf{meeting} := \; m_1 \vee  m_2 \vee  m_3 \vee  m_4 \vee  m_5 \vee  m_6 
% \end{empheq}
\end{align*}
$$
```bash
python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=14 --heuristics --heuristic_weight=100 --domain_file=./domain/domain_bosch.json  --domain=bosch --num_robots=6 --vis --print_step 
```
### Scenario 4 
Combinations of scenarios 1, 2 and 3

$$
\begin{align*}
 L_1: \quad &  \phi(1,1) =  \Diamond \phi(2,1) \wedge \Diamond\phi(2,2)  \wedge \Diamond\phi(2,3)\\
 L_2: \quad &  {\phi(2,1) =  \Diamond \phi(3,1) \wedge \Diamond\phi(3,2)} \\
            &  {\phi(2,2) =  \Diamond\phi(3,3) \wedge \Diamond\phi(3,4) \wedge \Diamond\phi(3,5)}\\
            &  {\phi(2,3) =  \Diamond\phi(3, 6) \wedge \Diamond\phi(3, 7) \wedge \Diamond\phi(3, 8)}\\
 L_3: \quad &  {\phi(3,1) = \Diamond (d_5 \wedge \mathsf{default}} \\ 
 &\quad \quad \quad \quad {\wedge \bigcirc ((\mathsf{carrybin}\; \mathcal{U}\; \mathsf{dispose}) \wedge \Diamond \mathsf{default}))}  \\ 
 & \quad \quad \quad \quad {\wedge \square (\mathsf{carrybin \Rightarrow \neg \mathsf{public}})}\\
                & {\phi(3,2) = \Diamond (d_5 \wedge \mathsf{emptybin} \wedge \bigcirc (d_5 \wedge \mathsf{default}))} \\
 & {\phi(3,3) = \Diamond (p \wedge \mathsf{carry}\; \mathcal{U}\; (d_{10} \wedge \bigcirc \neg \mathsf{carry}))} \\ 
 &\quad \quad \quad \quad {\wedge \square (\mathsf{carry} \Rightarrow \neg \mathsf{public})} \\
 &  {\phi(3,4) = \Diamond (p \wedge \mathsf{carry}\; \mathcal{U}\; (d_{7} \wedge \bigcirc \neg \mathsf{carry}))} \\ 
 &\quad \quad \quad \quad {\wedge \square (\mathsf{carry} \Rightarrow \neg \mathsf{public})}  \\
 &  {\phi(3,5) = \Diamond (p \wedge \mathsf{carry}\; \mathcal{U}\; (d_{5} \wedge \bigcirc \neg \mathsf{carry}))} \\ 
 &\quad \quad \quad \quad {\wedge \square (\mathsf{carry} \Rightarrow \neg \mathsf{public})}  \\ 
                & {\phi(3, 6) = \Diamond  \phi(4, 1) \wedge \Diamond  \phi(4, 2) \wedge \Diamond  \phi(4, 3)} \\
                  & { \phi(3, 7) = \Diamond (d_5 \wedge \mathsf{carry} \; \mathcal{U} \; (d_3 \wedge \bigcirc \neg \mathsf{carry}))} \\
  & \quad \quad \quad \quad {\wedge \square (\mathsf{carry} \Rightarrow \neg \mathsf{public})} \\
  &  {\phi(3, 8) = \Diamond (d_{11}\wedge \mathsf{guide} \; \mathcal{U}\; (m_6 \wedge \bigcirc \neg \mathsf{guide}))} \\
 L_4: \quad &  {\phi(4, 1) = \Diamond(m_1 \wedge \mathsf{photo}) \wedge \square (\neg \mathsf{meeting} \Rightarrow \neg \mathsf{camera} )} \\
 &  {\phi(4, 2) = \Diamond(m_4 \wedge \mathsf{photo})\wedge \square (\neg \mathsf{meeting} \Rightarrow \neg \mathsf{camera} )} \\
 &  {\phi(4, 3) = \Diamond(m_6 \wedge \mathsf{photo}) \wedge \square (\neg \mathsf{meeting} \Rightarrow \neg \mathsf{camera} )} \\
 & {\mathsf{meeting} := \; m_1 \vee  m_2 \vee  m_3 \vee  m_4 \vee  m_5 \vee  m_6   }
 \end{align*}
 $$
 ```bash
python hierarchical_LTL_stap_on_the_fly.py --task=nav --case=21 --heuristics --heuristic_weight=100 --domain_file=./domain/domain_bosch.json  --domain=bosch --num_robots=6 --vis --print_step 
```
# Citation
```
@article{luo2024simultaneous,
  title={Simultaneous Task Allocation and Planning for Multi-Robots under Hierarchical Temporal Logic Specifications},
  author={Luo, Xusheng and Liu, Changliu},
  journal={arXiv preprint arXiv:2401.04003},
  year={2024}
}
```