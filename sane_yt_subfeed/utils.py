def get_unicode_weight(text, unicode_weight_modifier):
    """
    Calculates a "width-weight" for unicode characters
    for use in things like text ellision().
    :param text: A string of text (unicode)
    :param unicode_weight_modifier: The modifier applied to weight calculations.
    :return:
    """
    unicode_weight = 0
    for c in text:
        if c == '「' or c == '」':
            # Weight extreme-width edge cases more than regular UTF-8
            unicode_weight += 16 * unicode_weight_modifier
        elif not c.isascii():
            unicode_weight += unicode_weight_modifier

    return unicode_weight
