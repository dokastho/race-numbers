import pandas as pd

numbers = dict()

def write_csv(df: pd.DataFrame):
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
        file_name = f'output/{race_name}.md'
        race_df.to_markdown(file_name)
        file_names.append(file_name)
        pass
    
    for file_name  in file_names:
        with open(file_name, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            file_name = file_name.rstrip('.md')
            file_name = file_name.lstrip('output/')
            f.write(f'# {file_name}' + '\n\n' + content)
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
        cat = int(row['USAC Category Road'].item())
        if cat is None:
            cat = 5
            pass

        is_junior = 'Junior' in row['Category Entered / Merchandise Ordered']
        if is_junior:
            cat = 6
            pass
        
        num = 1000 + (cat * 100) + number_counters[cat]
        racer_id = row.RacerID.item()
        if racer_id in numbers.keys():
            num = numbers[racer_id]
            pass
        else:
            numbers[racer_id] = num
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

    # add number column
    df['Race Number'] = None
    
    # assign None numbers to collegiate riders
    collegiates = set(df[df[race_str].str.contains('Collegiate')]['RacerID'])
    for race_id in list(collegiates):
        numbers[race_id] = None
        pass

    # sort by gender
    df = df.sort_values('Gender')

    # filter by maize and blue
    maize = df[df[race_str].str.contains('Maize')]
    blue = df[df[race_str].str.contains('Blue')]

    # filter by discipline (sunday only)
    blue_dom = blue[blue[race_str].str.contains('Domestic')]
    blue_col = blue[blue[race_str].str.contains('Collegiate')]

    # assign numbers to domestic riders
    blue_dom = add_race_numbers(blue_dom)

    # sort by category
    maize = maize.sort_values(cat_str)
    blue_col = blue_col.sort_values(cat_str)
    blue_dom = blue_dom.sort_values(cat_str)
    

    # filter by gender
    maize_m = maize[maize.Gender == 'M']
    maize_f = maize[maize.Gender == 'M']
    blue_dom_m = blue_dom[blue_dom.Gender == 'M']
    blue_dom_f = blue_dom[blue_dom.Gender == 'F']
    blue_col_m = blue_col[blue_col.Gender == 'M']
    blue_col_f = blue_col[blue_col.Gender == 'F']

    # write to output
    write_csv(maize_m)
    write_csv(maize_f)
    write_csv(blue_dom_m)
    write_csv(blue_dom_f)
    write_csv(blue_col_m)
    write_csv(blue_col_f)
    pass


if __name__ == "__main__":
    main()
