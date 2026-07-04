def train_one_parameter(x_values, y_values, weight, learning_rate, steps):
    for _ in range(steps):
        predictions = [weight * x for x in x_values]
        errors = [pred - target for pred, target in zip(predictions, y_values)]
        gradient = sum(error * x for error, x in zip(errors, x_values)) / len(x_values)
        weight = weight - learning_rate * gradient
    return weight
