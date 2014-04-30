cd cookedData
for file in *.csv
do
  split -l 50000 -d -a 4  "$file" "$file"
done
