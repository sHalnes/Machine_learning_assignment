#!/usr/bin/env python

'''INF283: Compulsory Assignment 1
test_ID3.py: implementation of ID3 learning algorithm'''

import math
import collections

__author__="Svetlana Halnes"

# We create two datasets from a file:
# training_data contains data which we're going to use for training
# test_data - the data we're going to use for test
training_data = []
test_data = []
with open('agaricus-lepiota.data') as fil:
    content = fil.read().split('\n')
    for i in range(len(content)):
        if content[i] != '' and i%2 > 0:
            training_data.append(content[i])
        else:
            if content[i] != '':
                test_data.append(content[i])
fil.close()

# decision tree is an ordered dictionary
dec_tree = collections.OrderedDict()
# dictionary for attributes
attr_dict = {}
# we're going to stop growing our tree when there is no more information gain can be found (so the gain == 0)
is_there_gain = True

log_fil = open("log.txt", 'w')
log_fil.write("\nProgram output\n")


def attributes():
    '''Create dictionary of attributes. Key = number of attr, value = all possible values'''
    dim = len(str(training_data[0]).split(','))
    for element in range(1, dim):
        s = []  # a temporary set for values
        for j in range(len(training_data)-1):
            line = training_data[j].split(',')
            if line[element] != '?':
                s.append(line[element])
        attr_dict[element] = set(s)


def positive_negative(column_1 = None, attr_1 = None, column_2 = None, attr_2 = None):
    '''Count how many positive and negative results has training data.
    If we have 2 parameters, the function counts positive and negative for this attribute
    If we have 4 parameters, then it counts for both attributes (for example: the number of yes/no
    for wind_strong if outlook_rainy ).'''
    poisonous = 0
    edible = 0

    if column_1 != None and attr_1 != None and column_2 != None and attr_2 != None:
        for d in range(len(training_data) - 1):
            line = str(training_data[d]).split(',')
            if line[column_1] == attr_1 and line[column_2] == attr_2 and line[0] == 'p':
                poisonous += 1
            elif line[column_1] == attr_1 and line[column_2] == attr_2 and line[0] == 'e':
                edible += 1
        return (poisonous, edible)

    elif column_1 != None and attr_1 != None and column_2 == None and attr_2 == None:
        for e in range(len(training_data)-1):
            line = str(training_data[e]).split(',')
            if line[column_1] == attr_1 and line[0] == 'p':
                poisonous += 1
            if line[column_1] == attr_1 and line[0] == 'e':
                edible += 1
        return (poisonous, edible)

    elif column_1 == None and attr_1 == None and column_2 == None and attr_2 == None:
        for k in range(len(training_data)-1):
            line = str(training_data[k]).split(',')
            if line[0] == 'p':
                poisonous += 1
            if line[0] == 'e':
                edible += 1
        return poisonous, edible

def countEntropy(yes, no, total_tests):
    '''Count the entropy
    :param yes, no, total_tests
    :return entropy '''
#    print('in count entropy')
    entropy = 0.0
    try:
        entropy = -(yes/total_tests)*math.log2(yes/total_tests) - (no/total_tests)*math.log2(no/total_tests)
    except:
        ValueError
    return entropy


def training_data_update(column, attribute):
    '''training data should be updated after every sucsessful iteration'''
    temp_training_data = []
    global training_data
    for line in training_data:
        line_content = str(line).split(',')
        if line_content[column] == attribute:
            temp_training_data.append(line)
    # here we change the whole training data
    training_data = temp_training_data
    #print(temp_training_data)

def decision_tree():
    '''Function makes a decision tree based on information gain'''
    # if the decision tree is empty
    keep_entr = [0.0, 0]# to keep entropy and number of yes/no
    if not any(dec_tree):
        # count the entropy
        yes, no = positive_negative()
        s = yes+no
        #total_tests = len(training_data)-1
        entropy_s = countEntropy(yes, no, s)
        #If keep_enrt[0]==0.0 -> we have a problem
        best_attr, keep_entr = choose_best_attr(entropy_s, s)
        key = best_attr.keys()
        values = list(best_attr.values())
        for k in key:
            for v in values:
                dec_tree[k] = v
    if any(dec_tree):
        global is_there_gain
        while any(attr_dict) and is_there_gain:
            items = list(dec_tree.items())
            target = items[-1]
            new_key = target[0]
            value = str(target[-1]).split()
            new_value = value[-1].strip('\' )')
            training_data_update(new_key, new_value)
            old_entropy = keep_entr[0]
            old_number_tests = keep_entr[1]
            keep_entr[0],keep_entr[1] = 0.0, 0.0
            while keep_entr[0] == 0.0 and any(attr_dict) and is_there_gain:
                best_attr, keep_entr = choose_best_attr(old_entropy, old_number_tests, new_key, new_value)
                if not any(best_attr):
                    is_there_gain = False
                key = best_attr.keys()
                values = list(best_attr.values())
                for k in key:
                    for v in values:
                        dec_tree[k] = v
    print('Our decision tree: ', dec_tree)
    log_fil.write('The decision tree is: ' + str(dec_tree))
    return dec_tree




def choose_best_attr(entropy_s, s, root_number = None, root_attr = None):
    best_attr = {}
    d_keys = attr_dict.keys()
    best_gain = 0.0
    keep_entr_numb = [0.0, 0.0]

    # if we need to find next best attribute
    if root_number != None and root_attr != None:
        entropy_temp = 1.0
        s_v_temp = 0.0
        for key in d_keys:
            best_value = ''
            next_best_value = ''
            gain = entropy_s
            d_values = list(attr_dict[key])
            for value in d_values:
                yes, no = positive_negative(int(key), value, int(root_number), root_attr)
                if no == 0:
                    best_value = value
                if yes == 0:
                    yes = 0
                    # I don't remember why I need this...
                else:
                    s_v = yes + no
                    entropy_s_v = countEntropy(yes, no, s_v)
                    if 0.0 < entropy_s_v < entropy_temp:
                        entropy_temp = entropy_s_v
                        next_best_value = value
                        s_v_temp = s_v
                    gain -= (s_v/s * entropy_s_v)

            if gain > best_gain:
                best_gain = gain
                if any(best_attr):
                    best_attr.clear()
                if best_value != "" and next_best_value != "":
                    best_attr[key] = best_value, next_best_value
                    keep_entr_numb[0] = entropy_temp
                    keep_entr_numb[1] = s_v_temp
                elif best_value != "" and next_best_value == "":
                    keep_entr_numb[0] = 0.0
                    keep_entr_numb[1] = 0.0
                    best_attr[key] = best_value
                else:
                    best_attr[key] = next_best_value
        # we need to delite the best attribute from attr_dict
        key_to_delite = best_attr.keys()
        for k in key_to_delite:
            del attr_dict[k]
        return best_attr, keep_entr_numb

    # for the first call of the function
    else:
        entropy_temp = 1.0
        for key in d_keys:
            best_value = ''
            next_best_value = ''
            gain = entropy_s
            d_values = list(attr_dict[key])
            for value in d_values:
                yes, no = positive_negative(int(key), value)
                if no == 0:
                    best_value = value
                s_v = yes + no
                entropy_s_v = countEntropy(yes, no, s_v)
                if 0.0 < entropy_s_v < entropy_temp:
                    entropy_temp = entropy_s_v
                    next_best_value = value
                    keep_entr_numb[0] = entropy_temp
                    keep_entr_numb[1] = s_v
                gain -= (s_v/s * entropy_s_v)
            if gain > best_gain:
                best_gain = gain
                if any(best_attr):
                    best_attr.clear()
                    if best_value != "":
                        best_attr[key] = best_value, next_best_value
                    else:
                        best_attr[key] = next_best_value
                else:
                    if best_value != "":
                        best_attr[key] = best_value, next_best_value
                    else:
                        best_attr[key] = next_best_value
        # we need to delite the best attribute from attr_dict
        key_to_delite = best_attr.keys()
        for k in key_to_delite:
            del attr_dict[k]
        return best_attr, keep_entr_numb


def tree_test(dec_tree):
    output_data = []
    log_fil.write("\nTest data with the decision tree classification\n")
    for line in test_data:
        line_content = str(line).split(',')
        #change the first attribute to check later
        line_content[0] = 'U'
        for keys, values in dec_tree.items():
            # only one attribute
            if len(values) == 1 and line_content[int(keys)] == values[0]:
                line_content[0] = 'p'
                break

            elif len(values) > 1 and line_content[int(keys)] == values[0]:
                line_content[0] = 'p'
                break

            elif len(values) > 1 and line_content[int(keys)] != values[1]:
                line_content[0] = 'e'
                break
        output_data.append(line_content)
        log_fil.write(str(line_content)+'\n')
    return output_data


def compare_results(output_data):
    '''Here we're going to go through output file and test data and compare results'''
    test_number = len(output_data)
    print("\nThe number of tests: ", test_number)
    log_fil.write("\nThe number of tests: " + str(test_number))
    counter = 0
    for i in range(test_number-1):
        out_line = output_data[i]
        data_line = str(test_data[i]).split(',')
        if out_line[0] == data_line[0]:
            counter += 1
    err = (test_number - counter)/test_number
    conf_interval = math.sqrt((err * (1 - err))/test_number)
    print('Number of matches: ', counter, '\nError(h) = ', round(err, 4), '\nConfidence intervall = ',
          round(err, 4), '+/-', round(conf_interval, 4))
    log_fil.write('\nNumber of matches: ' + str(counter) + '\nError(h) = ' + str(round(err, 4)) + '\nConfidence intervall = ' +
          str(round(err, 4)) + '+/-' + str(round(conf_interval, 4)))



def main():
    print("\nLet's start testing...\n")
    attributes()
    dec_tree = decision_tree()
    log_fil.write('\nA branch with just one attribute is a leaf with all positive results \n(here it means that the mushroom is poisonous)')
    print('\nA branch with just one attribute is a leaf with all positive results \n(here it means that the mushroom is poisonous)')
    output_data = tree_test(dec_tree)
    compare_results(output_data)


if __name__ == '__main__':
    main()