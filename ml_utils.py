import numpy as np

def normalize(X, mean, std):
    """
    Normalizes the input array X by subtracting the mean and dividing by the standard deviation.

    Parameters
    ----------
    X : numpy.ndarray
        The input data to be normalized. It should be a NumPy array of any shape, typically used for 
        features in machine learning models. Each element in X is modified in place.
    
    mean : numpy.ndarray or float
        The mean value(s) to subtract from X. This can either be:
        - A scalar (float) representing the mean to subtract from all elements of X.
        - A NumPy array of the same shape as X, or broadcastable to the shape of X, where each
          element in X will have the corresponding mean subtracted.
    
    std : numpy.ndarray or float
        The standard deviation value(s) to divide X by. This can either be:
        - A scalar (float) representing the standard deviation for all elements of X.
        - A NumPy array of the same shape as X, or broadcastable to the shape of X, where each
          element in X will be divided by the corresponding standard deviation.

    Returns
    -------
    None
        This function modifies the input array `X` in place and does not return a value.

    Example
    -------
    >>> import numpy as np
    >>> X = np.array([1.0, 2.0, 3.0, 4.0])
    >>> mean = np.mean(X)
    >>> std = np.std(X)
    >>> normalize(X, mean, std)
    >>> print(X)
    array([-1.34164079, -0.4472136 ,  0.4472136 ,  1.34164079])

    """
    X -= mean
    X /= std


def kfold(tr_X, tr_Y, k, create_compile_fit, metric='val_loss'):
    """
    Performs K-Fold cross-validation on a dataset and returns the validation metric for each fold.

    This function splits the dataset into `k` subsets (folds) for cross-validation. In each iteration, 
    one fold is used as the validation set while the remaining `k-1` folds are used for training. The 
    model is trained and validated `k` times, and the specified validation metric (e.g., validation loss) 
    from each fold is collected.

    Parameters
    ----------
    tr_X : numpy.ndarray
        The input training data. It should be a NumPy array where each row is an example, and each column 
        is a feature. The dataset is split into `k` folds.
    
    tr_Y : numpy.ndarray
        The training labels corresponding to `tr_X`. It should be a NumPy array where each element 
        represents the label for the corresponding row in `tr_X`.
    
    k : int
        The number of folds for cross-validation. This determines how many subsets the dataset is divided 
        into for training and validation.

    create_compile_fit : callable
        A function that, when called, compiles a model, trains it on the training folds, validates it on 
        the validation fold, and returns a history object that includes the specified validation metric 
        (e.g., `val_loss`). This function should accept four parameters: training data (`trk_X`), 
        training labels (`trk_Y`), validation data (`v_X`), and validation labels (`v_Y`).
    
    metric : str, optional
        The name of the validation metric to retrieve from the history object returned by 
        `create_compile_fit`. By default, this is set to `'val_loss'`, but it can be any other metric 
        (e.g., `'val_accuracy'`) depending on the model's history.

    Returns
    -------
    val_metrics : list of float
        A list containing the final value of the specified validation metric for each fold. 
        The length of the list is `k`, and each element corresponds to the value of the `metric` 
        (e.g., validation loss or validation accuracy) for one of the `k` folds.

    Notes
    -----
    - The function handles cases where the number of examples in `tr_X` is not perfectly divisible by `k`. 
      In such cases, the remainder examples are distributed evenly among the last folds.
    - In each fold, the function splits the data into training and validation sets, trains the model, 
      and retrieves the final value of the specified validation metric.
    - The `create_compile_fit` function should return a history object (e.g., a dictionary containing 
      training and validation losses/metrics) from which the specified `metric` is extracted.

    Example
    -------
    Suppose `create_compile_fit` is a function that compiles, trains, and validates a machine learning model, 
    and returns a history dictionary. Here's how to use the function:

    >>> import numpy as np
    >>> def create_compile_fit(trk_X, trk_Y, v_X, v_Y):
    ...     # Example of returning a history dictionary with 'val_loss'
    ...     return {'val_loss': [0.5, 0.4, 0.35, 0.3]}  # Simulated training history for example purposes

    >>> tr_X = np.random.rand(100, 10)  # 100 examples, 10 features
    >>> tr_Y = np.random.randint(0, 2, size=100)  # 100 binary labels

    >>> val_metrics = strat_kfold(tr_X, tr_Y, 10, 5, create_compile_fit, metric='val_loss')
    >>> print(val_metrics)
    [0.3, 0.3, 0.3, 0.3, 0.3]  # Example output

    """

    num_examples = tr_X.shape[0]
    val_examples_per_fold = num_examples // k
    remainder = num_examples % k
    val_metrics = []
    val_start = 0
    val_end = val_examples_per_fold
    for i in range(k-remainder):
        v_X = tr_X[val_start:val_end]
        v_Y = tr_Y[val_start:val_end]

        trk_X = np.vstack((tr_X[:val_start], tr_X[val_end:]))
        trk_Y = np.concatenate((tr_Y[:val_start], tr_Y[val_end:]))

        history = create_compile_fit(trk_X, trk_Y, v_X, v_Y)

        val_metrics.append(history[metric][-1])

        val_start = val_end
        val_end = val_end + val_examples_per_fold


    val_end = val_end + 1
    for i in range(k-remainder, k): # if we have extra examples (n//k is not an integer), just distribute them evenly amongst last folds
        v_X = tr_X[val_start:val_end]
        v_Y = tr_Y[val_start:val_end]

        trk_X = np.vstack((tr_X[:val_start], tr_X[val_end:]))
        trk_Y = np.concatenate((tr_Y[:val_start], tr_Y[val_end:]))

        history = create_compile_fit(trk_X, trk_Y, v_X, v_Y)

        val_metrics.append(history[metric][-1])

        val_start = val_end
        val_end = val_end + val_examples_per_fold + 1
    
    return val_metrics

def strat_kfold(tr_X, tr_Y, n, k, create_compile_fit, metric='val_loss'):
    """
    Performs multiple (n) k-fold cross-validations on a dataset and returns n*k validation metrics
    for each fold.

    In each iteration, the data is shuffled before starting the folds

    Parameters
    ----------
    tr_X : numpy.ndarray
        The input training data. It should be a NumPy array where each row is an example, and each column 
        is a feature. The dataset is split into `k` folds.
    
    tr_Y : numpy.ndarray
        The training labels corresponding to `tr_X`. It should be a NumPy array where each element 
        represents the label for the corresponding row in `tr_X`.
    
    n : int
        The number of time to run cross-validation.   

    k : int
        The number of folds for cross-validation. This determines how many subsets the dataset is divided 
        into for training and validation.

    create_compile_fit : callable
        A function that, when called, compiles a model, trains it on the training folds, validates it on 
        the validation fold, and returns a history object that includes the specified validation metric 
        (e.g., `val_loss`). This function should accept four parameters: training data (`trk_X`), 
        training labels (`trk_Y`), validation data (`v_X`), and validation labels (`v_Y`).
    
    metric : str, optional
        The name of the validation metric to retrieve from the history object returned by 
        `create_compile_fit`. By default, this is set to `'val_loss'`, but it can be any other metric 
        (e.g., `'val_accuracy'`) depending on the model's history.

    Returns
    -------
    val_metrics : list of float
        A list containing the final value of the specified validation metric for each fold. 
        The length of the list is `k`, and each element corresponds to the value of the `metric` 
        (e.g., validation loss or validation accuracy) for one of the `k` folds.

    Notes
    -----
    - The function handles cases where the number of examples in `tr_X` is not perfectly divisible by `k`. 
      In such cases, the remainder examples are distributed evenly among the last folds.
    - In each fold, the function splits the data into training and validation sets, trains the model, 
      and retrieves the final value of the specified validation metric.
    - The `create_compile_fit` function should return a history object (e.g., a dictionary containing 
      training and validation losses/metrics) from which the specified `metric` is extracted.

    Example
    -------
    Suppose `create_compile_fit` is a function that compiles, trains, and validates a machine learning model, 
    and returns a history dictionary. Here's how to use the function:

    >>> import numpy as np
    >>> def create_compile_fit(trk_X, trk_Y, v_X, v_Y):
    ...     # Example of returning a history dictionary with 'val_loss'
    ...     return {'val_loss': [0.5, 0.4, 0.35, 0.3]}  # Simulated training history for example purposes

    >>> tr_X = np.random.rand(100, 10)  # 100 examples, 10 features
    >>> tr_Y = np.random.randint(0, 2, size=100)  # 100 binary labels

    >>> val_metrics = strat_kfold(tr_X, tr_Y, 10, 5, create_compile_fit, metric='val_loss')
    >>> print(val_metrics)
    [0.3, 0.3, 0.3, 0.3, 0.3]  # Example output

    """
    val_metrics = []
    num_examples = tr_X.shape[0]
    for i in range(n):
        perm_index = np.random.permutation(num_examples)
        tr_X = tr_X[perm_index]
        tr_Y = tr_Y[perm_index]
        val_metrics.extend(kfold(tr_X, tr_Y, k, create_compile_fit, metric))
    return val_metrics

def coefficient_of_variation(tr_X, tr_Y, create_compile_fit, val_split_percentage, num_tests):
    """
    Computes the coefficient of variation (CV) of validation loss over multiple training iterations 
    with random data shuffling.

    The coefficient of variation is defined as the ratio of the standard deviation to the mean of 
    the validation loss across different runs. This function trains a model multiple times using 
    different data shuffles and calculates the CV to assess the consistency of the model's validation 
    performance.

    Parameters
    ----------
    tr_X : numpy.ndarray
        The input training data. This should be a NumPy array where each row represents an example, 
        and each column represents a feature. This data will be shuffled during the function execution.
    
    tr_Y : numpy.ndarray
        The training labels corresponding to `tr_X`. This should be a NumPy array where each element 
        is the label for the corresponding row in `tr_X`. It will be shuffled in tandem with `tr_X`.
    
    create_compile_fit : callable
        A function that, when called, compiles a model, fits it to the training data, and returns 
        a history object containing the validation loss (`history['val_loss']`). This function is 
        expected to run the entire model training and validation process, including any callbacks or 
        epochs defined within it.
    
    val_split_percentage : float
        The percentage of the data to be used as validation data. This should be a float between 0 and 1.
        For example, `val_split_percentage = 0.8` means 20% of the data will be used for validation, and 
        80% will be used for training in each test run.
    
    num_tests : int
        The number of times to repeat the training process with different random shuffles of the data. 
        The validation loss from each iteration will be used to compute the coefficient of variation.

    Returns
    -------
    coeff_of_variation : float
        The coefficient of variation (CV) of the validation loss across the `num_tests` iterations.
        CV is calculated as the ratio of the standard deviation of validation losses to the mean of 
        validation losses. A higher CV indicates greater variability in the model's validation 
        performance, while a lower CV suggests more consistent performance.

    Notes
    -----
    - In each iteration, the function splits the training data into a training set and a validation set 
      based on `val_split_percentage`.
    - The data is shuffled before each iteration to ensure random splits between training and validation 
      sets, which helps test the robustness of the model across different data arrangements.
    - After each test, the validation loss is collected and used to calculate the mean and standard deviation.
    - The coefficient of variation can be useful in assessing model stability, particularly in scenarios 
      where validation performance varies significantly depending on the split of training data.

    Example
    -------
    Suppose `create_compile_fit` is a function that compiles and trains a machine learning model, 
    and returns a history dictionary with `val_loss`. Here's how you could use the function:

    >>> import numpy as np
    >>> def create_compile_fit(tr_X, tr_Y, v_X, v_Y):
    ...     # Dummy example of returning a history dictionary with 'val_loss'
    ...     return {'val_loss': [0.4, 0.35, 0.32, 0.3]}  # Example of a typical training history

    >>> tr_X = np.random.rand(1000, 10)  # 1000 examples, 10 features
    >>> tr_Y = np.random.randint(0, 2, size=1000)  # 1000 binary labels

    >>> cv = coefficient_of_variation(tr_X, tr_Y, create_compile_fit, 0.2, 5)
    >>> print(cv)
    0.0456  # Example output

    """
    num_examples = tr_X.shape[0]
    val_split = int(val_split_percentage*num_examples)
    val_losses = []
    for i in range(num_tests):
        random_indicies = np.random.permutation(num_examples)
        tr_X = tr_X[random_indicies]
        tr_Y = tr_Y[random_indicies]

        v_X = tr_X[val_split:]
        v_Y = tr_Y[val_split:]

        tr_X = tr_X[:val_split]
        tr_Y = tr_Y[:val_split]

        history = create_compile_fit(tr_X, tr_Y, v_X, v_Y)

        val_losses.append(history['val_loss'][-1])

        tr_X = np.vstack((tr_X, v_X))
        tr_Y = np.concatenate((tr_Y, v_Y))

    mean_val_loss = np.mean(val_losses)
    std_val_loss = np.std(val_losses)

    coeff_of_variation = std_val_loss / mean_val_loss

    return coeff_of_variation