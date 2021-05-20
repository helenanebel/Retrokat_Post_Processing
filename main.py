from transform_MARCXML import transform, check_and_split_in_issues

if __name__ == '__main__':
    # check_and_split_in_issues()
    transform('145', [r'Presenting\sthe', r'Index\sto', r'Book\sReview:\sBooks\sReceived', r'Cumulative\sIndex\sVolumes\sI-XV\s(1971–1985)', r'Other\sBooks\sReceived'],
              (1971, 2017))