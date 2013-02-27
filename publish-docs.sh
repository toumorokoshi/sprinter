# this requires sphinx to be installed:
# $ easy_install -U sphinx
cd docs
make html
git checkout gh-pages
cd ..
rm -rf _*
mv docs/build/html/* .
git add .
git commit -am "build $(date)"
git push origin gh-pages
git checkout master
