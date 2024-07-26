def database_description(database_url):
    table_list = runcmd_list(
        [
            "psql",
            database_url,
            "-c",
            f"\d",
        ],
        quiet = True,
    )
    commands = [] 
    for line in table_list[3 : len(table_list) - 2]:
        table_name = line.split("|")[1].strip()
        commands.append([
            "psql",
            database_url,
            "-c",
            f"\d {table_name}",
        ])
    descriptions = parallel_v2(commands, runcmd_list_async)
    description_2 = runcmd_list(
        [
            "psql",
            database_url,
            "-c",
            """
            select n.nspname as enum_schema,  
                t.typname as enum_name,  
                e.enumlabel as enum_value
            from pg_type t
                join pg_enum e on t.oid = e.enumtypid  
                join pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            order by enum_schema, enum_name, enum_value
            ;
        """,
        ]
    )
    return (
        "Tables:\n" + "\n".join(descriptions) + "\nEnums:\n" + "\n".join(description_2)
    )
