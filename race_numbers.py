import pandas as pd
import math

numbers = dict()

html_content = """<!DOCTYPE html>
<html>
<head>
<style>
h1 {
  font-family: Arial  
}

.dataframe {
  font-family: Arial, Helvetica, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

.dataframe td, .dataframe th {
  border: 1px solid #ddd;
  padding: 8px;
}

.dataframe tr:nth-child(even){background-color: #f2f2f2;}

.dataframe tr:hover {background-color: #ddd;}

.dataframe th {
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #04AA6D;
  color: white;
}
</style>
</head>
<body>
"""


def roundup(x):
    return int(math.ceil(x / 100.0)) * 100


def get_rider_name(row):
    fname: str = row["First Name"].item()
    lname: str = row["Last Name"].item()
    rider_name = fname.upper() + " " + lname.upper()
    return rider_name


def load_collegiate_numbers():
    col_nums_filename = 'just_bibs.csv'
    df = pd.read_csv(col_nums_filename)
    for index, row in df.iterrows():
        row = df[df.index == index]
        if sum(row.isnull().any()) == 3:
            continue
        rider_name = get_rider_name(row)
        race_num = row["Race Number"].item()
        if rider_name in numbers.keys():
            old_race_num = numbers[rider_name]
            did_cat_up = roundup(old_race_num) != roundup(race_num)
            if did_cat_up:
                continue
            pass
        numbers[rider_name] = race_num
        pass
    pass


def write_html(df: pd.DataFrame):
    race_names = list(set(df['Category Entered / Merchandise Ordered']))
    df = df[[
        'Race Number',
        'Last Name',
        'First Name',
        'Team',
        'Phone',
        'Emergency Contact',
        'Emergency Phone',
        'USAC License',
        'ZIP',
        'USAC Category Road',
        'Category Entered / Merchandise Ordered'
    ]]

    race_name: str

    file_names: 'list[str]' = []
    for race_name in race_names:
        race_df: pd.DataFrame = df[df['Category Entered / Merchandise Ordered'] == race_name]
        race_name = race_name.replace('/', ' ')
        file_name = f'output/{race_name}.html'
        race_df.to_html(file_name)
        file_names.append(file_name)
        pass

    for file_name in file_names:
        with open(file_name, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            file_name = file_name.rstrip('html')
            file_name = file_name.rstrip('.')

            file_name = file_name.lstrip('output/')
            f.write(f'{html_content}<h1>{file_name}</h1>' + '\n\n' +
                    content.replace('None', '    ') + "\n</body>")
        pass

    pass


def write_domestic_numbers(df: pd.DataFrame):
    cats = list(set(df['USAC Category Road']))

    for cat in cats:
        # filter by category
        cat_df: pd.DataFrame = df[df['USAC Category Road'] == cat]

        # remove collegiate
        cat_df = cat_df[cat_df['Category Entered / Merchandise Ordered'].str.contains('Domestic')]
        
        # remove collegiate participants
        cat_df = cat_df[cat_df['Race Number'] >= 1000]

        # pick columns
        cat_df = cat_df[[
            'Race Number',
            'USAC License',
            'Last Name',
            'First Name',
            'Team',
            'USAC Category Road'
        ]]

        # drop duplicates
        cat_df = cat_df.drop_duplicates()

        # write CSV
        cat_df.to_csv(f'output/domestic-cat-{cat}.csv')
        pass

    pass


def add_race_numbers(df: pd.DataFrame) -> pd.DataFrame:
    number_counters = dict({
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
    })
    for idx in list(df.index):
        row = df[df.index == idx]
        cat = 5.0
        cat_row = row['USAC Category Road']
        if not cat_row.isnull().any():
            cat = cat_row.item()
            pass

        is_junior = 'Junior' in row['Category Entered / Merchandise Ordered'].item()
        if is_junior:
            cat = 6
            pass

        num = 1000 + (cat * 100) + number_counters[cat]
        rider_name = get_rider_name(row)
        if rider_name in numbers.keys():
            num = numbers[rider_name]
            pass
        else:
            numbers[rider_name] = num
            number_counters[cat] += 1
            pass

        df.loc[idx, 'Race Number'] = num
        pass

    return df

# USAC License, Last Name, First Name, ZIP, Phone, Team, Category Entered / Merchandise Ordered, Emergency Contact, Emergency Phone, Race Number


def main():
    filename: str = "registrants.csv"
    race_str: str = "Category Entered / Merchandise Ordered"
    cat_str: str = "USAC Category Road"
    df = pd.read_csv(filename)

    # load existing numbers into `numbers`
    load_collegiate_numbers()

    # add number column
    df['Race Number'] = None

    # assign None numbers to collegiate riders who aren't in the USAC file
    collegiates = df[df[race_str].str.contains('Collegiate')]
    rider_names: 'list[str]' = []
    for index, row in collegiates.iterrows():
        row = df[df.index == index]
        if sum(row.isnull().any()) == 3:
            continue
        rider_name = get_rider_name(row)
        rider_names.append(rider_name)
        pass

    rider_names = list(set(rider_names))

    for rider_name in rider_names:
        if rider_name not in numbers.keys():
            numbers[rider_name] = None
        pass

    # sort by gender
    df = df.sort_values('Gender')

    # assign numbers to riders
    df = add_race_numbers(df)

    # filter by maize and blue
    maize = df[df[race_str].str.contains('Maize')]
    blue = df[df[race_str].str.contains('Blue')]

    # filter by discipline (sunday only)
    blue_dom = blue[blue[race_str].str.contains('Domestic')]
    blue_col = blue[blue[race_str].str.contains('Collegiate')]

    # sort by category
    maize = maize.sort_values(cat_str)
    blue_col = blue_col.sort_values(cat_str)
    blue_dom = blue_dom.sort_values(cat_str)

    # filter by gender
    maize_m = maize[maize.Gender == 'M']
    maize_f = maize[maize.Gender == 'F']
    blue_dom_m = blue_dom[blue_dom.Gender == 'M']
    blue_dom_f = blue_dom[blue_dom.Gender == 'F']
    blue_col_m = blue_col[blue_col.Gender == 'M']
    blue_col_f = blue_col[blue_col.Gender == 'F']

    # write to output
    write_html(maize_m)
    write_html(maize_f)
    write_html(blue_dom_m)
    write_html(blue_dom_f)
    write_html(blue_col_m)
    write_html(blue_col_f)

    # save domestic number assignments
    write_domestic_numbers(df)
    pass


if __name__ == "__main__":
    main()
