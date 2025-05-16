#!/usr/bin/env bash
for n in src/*/*.py; do
    module_name="${n##*src/}"
    module_name="${module_name%.py}"
    module_name="${module_name/\//.}"

    if [[ "${module_name}" =~ "__init__" || "${module_name}" =~ "__about__" ]]; then
        continue
    fi

    echo "creating docs for: ${module_name}"
    cat << EOF > "docs/modules/${module_name}.rst"
============================
\`\`${module_name}\`\`
============================

.. automodule:: ${module_name}

EOF
done
