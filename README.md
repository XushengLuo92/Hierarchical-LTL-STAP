# Hierarchical-LTL-STAP
Here is an example of the task description and the HTN tree of this task. do not directly copy them. You are suggested the HTN tree has multiple levels, and each leaf node of same father have something in common, please remember this feature in following tasks.
The requirement on HTN structure is that ensure that the end nodes (or leaf nodes) of the tree represent primitive tasks or facts. These primitive tasks should be described as simply as possible, avoiding any use of logical terms. If they do contain such terms, it indicates that the task can be broken down further. Typically, these basic descriptions are brief phrases. If a task seems too intricate for a leaf node, it's a sign that there might be underlying subtasks, and you should delve deeper by expanding that node. Remember, the collective meaning of all the subtasks under a parent node should align with the overall meaning of that parent node.

The example task description is "There are three kinds of different blocks on the table, you are suggested to plate them into the box, remember that the red, yellow, blue blocks should be in different boxes. If there is no red blocks, speak it out. After that, remove all of the boxes into the drawer",
The HTN is 
1. Place different blocks into boxes and remove them into the drawer
    1.1 Place blocks into boxes
       1.1.1 Place red blocks into boxes if they exist, otherwise speak it out
         1.1.1.1 Place red blocks into boxes if they exist
         1.1.1.2 Speak it out if red blocks does not exist
       1.1.2 Place yellow blocks into boxes
       1.1.3 Place blue blocks into boxes
    1.2 Remove boxes into the drawer
       1.2.1 Place the box with red blocks into the drawer
       1.2.2 Place the box with yellow blocks into the drawer
       1.2.3 Place the box with blue blocks into the drawer
Write the following HTN into JOSN format. Each subtask is mapped into a JSON block as 
 "Task_1": {
      "task_id": "prop_1",
      "task_description": "Place different blocks into boxes and remove them into the drawer",
      "task_relied_sentence": "There are three kinds of different blocks on the table, you are suggested to plate them into the box, remember that the red, yellow, blue blocks should be in different boxes. After that, remove all of the boxes into the drawer",
      "temporal_relation_of_subtasks": "",
      "subtasks_of_this_node":  {}
}
where "Task_1" denotes the hierarchy level, "task_id" is the unique id, "task_description" summarize the task along with all of its subtasks, "task_relied_sentence" is the part of sentence corresponding to this task_1, "temporal_relation_of_subtasks" denote the temporal relation between this task_1 with other tasks that have the same hierarchy level in HTN, "subtasks_of_this_node" is the set of subtasks that "Task_1" is decomposed into, where each subtask use the identical JSON block. 
Here is another example task" You are suggested to help in shopping, you will pick beef, chicken and apples if you find them. if you pick beef, you are suggested to pick a carrots. if there is no beef, you will pick egges and a potato. Finally, you will have to check out and Place what you picked in three bags according a classification of meat, vegetables and fruits"
Translate it into HTN and JSON format.
