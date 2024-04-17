# %%

import pandas as pd
import os

etudes = pd.read_json("etudes.json")
pieces = pd.read_json("pieces.json")

etudes["Type"] = "etude"
pieces["Type"] = "piece"
annotations = pd.concat([etudes, pieces])

# %%
# * From violin transcription paper
import os
import yaml
import glob
# * gen paganini
dataset = os.path.join('..', '..', 'violin-transcription', 'dataset', '*', '*.mid*')
dataset = glob.glob(dataset)
grand_parent = "Etudes"
items = []
for item in dataset:
    item = os.path.basename(item)
    item = item.rsplit('.')[0]
    composer, op, player, yt_id = item.split('_', 3)
    yt_id, start, end = yt_id.rsplit('-', 2)
    start = int(start)
    end = int(end)
    title = ', '.join((composer, ', No. '.join(op.split('-', 1))))
    parent = composer
    permalink = "_".join([composer, op])
    md = '    {% include sample.html ' + f'player="{player}" id="{yt_id}" start={start} end={end}' + ' %}'
    items.append({'parent': parent, 'grand_parent': grand_parent, 'title': title, 'md': md, 'permalink': permalink})
items = pd.DataFrame(items)
# %%
grouped = items.groupby(['grand_parent'])

for i, (grand_parent, gp_group) in enumerate(grouped):
    # Create a new directory for each grand_parent
    grand_parent_dir = os.path.join('..', 'docs', grand_parent)
    os.makedirs(grand_parent_dir, exist_ok=True)

    gp_md_file = os.path.join(grand_parent_dir, f'{grand_parent}.md')
    if not os.path.exists(gp_md_file):
        # Create a new markdown file for each grand_parent
        with open(gp_md_file, 'w') as new_file:
            front_matter = {
                'layout': 'default',
                'title': grand_parent,
                'nav_order': i,
                'has_children': True,
                'permalink': f"/docs/{grand_parent.replace(' ', '_')}",
            }
            new_file.write(f'---\n{yaml.dump(front_matter)}---\n# {grand_parent}\n')

    # Group the items by parent within the current grand_parent group
    parent_grouped = gp_group.groupby('parent')

    # Create a new markdown file for each parent in the group
    for j, (parent, p_group) in enumerate(parent_grouped, start=1):
        # Create a new directory for each parent
        parent_dir = os.path.join(grand_parent_dir, parent)
        os.makedirs(parent_dir, exist_ok=True)

        # Create a new markdown file for each parent
        with open(os.path.join(parent_dir, f'{parent}.md'), 'w') as new_file:
            front_matter = {
                'layout': 'default',
                'title': parent,
                'parent': grand_parent,
                'nav_order': j,
                'has_children': True,
                'permalink': f"/docs/{grand_parent.replace(' ', '_')}/{parent.replace(' ', '_')}"
            }
            new_file.write(f'---\n{yaml.dump(front_matter)}---\n# {parent}\n')

        # Sort the parent_group by title
        title_grouped = p_group.groupby('title')
        
        # Create a new markdown file for each title in the parent_group
        for k, (title, t_group) in enumerate(title_grouped, start=1):
            permalink = t_group['permalink'].iloc[0]
            front_matter = {
                'layout': 'default',
                'title': title,
                'parent': parent,
                'grand_parent': grand_parent,
                'nav_order': k,
                'permalink': f"/docs/{grand_parent.replace(' ', '_')}/{permalink}"
            }
            content = f'---\n{yaml.dump(front_matter)}---\n'
            content += f'# Performances\n<div class="sample-container">\n'
            for _, row in t_group.iterrows():
                content += row.md + '\n'
            content += '</div>'
            with open(os.path.join(parent_dir, f'{permalink}.md'), 'w') as new_file:
                new_file.write(content)



# %%
