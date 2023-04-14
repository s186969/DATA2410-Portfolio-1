#   The overall thesis of this task is to create a formula that can calculate Jain's Fairness Index by 
#   taking in two throughput values. 

#   The Fairness Index is given by:
#   f(x) = [(sum x_i)**2] / n*sum[(x_i)**2]

#   The function that calculates the Jain's Fairness Index.



def jains(num1, num2):
    numerator = (int(num1) + int(num2))                     #   Sum of the numerator
    denominator = (int(num1)**2+int(num2)**2)               #   Denominator, sum of the values with the power of two

    result = (numerator**2) / (2*denominator)               #   Numerator, power of two, divided by the amount of values times denominator
    return result                                           #   Returns the index

while True:
    try: 
        num1 = 26.26
        num2 = 18.52

        if num1 <= 0 or num2 <= 0:
            print("Feilmelding: Du har skrevet et tall som er lik eller mindre enn null. Du må skrive inn et naturlig heltall!")
        else:
            output = jains(num1, num2)                          #   The Jain's Fairness Index
            print("JFI: ", output)                              #   The message
            break
    except ValueError:
        print("Feilmelding: Du må skrive inn et naturlig heltall!")                                          #   Returns the index

