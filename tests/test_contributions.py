import unittest, tempfile,json
from pathlib import Path
from review_contributions import validate,import_directory
R={'schema':'jam-archive-contribution-v1','kind':'recording_source','subject':'The Allman Brothers Band - Fillmore East','date':'1971-03-12','source_url':'https://archive.org/details/example','details':'Possible audience recording; date and set identification require verification.','credit':'','status':'pending_review','submitted_at':'2026-10-26T00:00:00Z'}
class ContributionTests(unittest.TestCase):
    def test_valid(self):self.assertEqual(validate(R)['kind'],'recording_source')
    def test_bad_source(self):
        with self.assertRaises(ValueError):validate({**R,'source_url':'http://bad.example'})
    def test_bad_evidence(self):
        with self.assertRaises(ValueError):validate({**R,'details':'guess'})
    def test_bad_date(self):
        with self.assertRaises(ValueError):validate({**R,'date':'1971-02-31'})
    def test_import_and_dedupe(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'submitted';folder.mkdir();out=Path(tmp)/'review'
            (folder/'one.json').write_text(json.dumps(R))
            self.assertEqual(import_directory(folder,out)[:2],(1,0))
            self.assertEqual(import_directory(folder,out)[:2],(0,1))
            self.assertEqual(len(list(out.glob('*.json'))),1)
if __name__=='__main__':unittest.main()
