def max_freq(lst):
    freq ={}
    for i in lst:
        if i in freq:
            freq[i] += 1
        else:
            freq[i]=1

    temp= []
    for j in freq:
        if freq[j]==j:
            temp.append(j)

    return max(temp) if temp else -1
print(max_freq([1, 1, 2, 2, 3, 3, 3]))