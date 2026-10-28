import json,sqlite3,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import research_agent as a

class AgentTests(unittest.TestCase):
    def setUp(self):
        self.ctx=tempfile.TemporaryDirectory()
        self.db=a.connect(Path(self.ctx.name)/'state.sqlite')
        self.cat=a.catalog()
    def tearDown(self):
        self.db.close();self.ctx.cleanup()
    def test_exact_show_match_still_requires_review(self):
        row={'candidate_type':'recording','provider':'test','external_id':'alpha','artist_id':'grateful-dead',
             'title':'Test record','observed_date':'1977-05-08','source_url':'https://archive.org/details/etree'}
        id=a.ingest(self.db,self.cat,row);r=self.db.execute('SELECT * FROM candidate WHERE id=?',(id,)).fetchone()
        self.assertEqual(r['status'],'pending');self.assertEqual(r['proposed_show_id'],'gd-1977-05-08')
    def test_two_fillmore_performances_remain_ambiguous(self):
        row={'candidate_type':'recording','provider':'test','external_id':'beta','artist_id':'the-allman-brothers-band',
             'title':'Test record','observed_date':'1971-03-12','source_url':'https://allmanbrothersband.com/shows/'}
        id=a.ingest(self.db,self.cat,row);r=self.db.execute('SELECT * FROM candidate WHERE id=?',(id,)).fetchone()
        self.assertIsNone(r['proposed_show_id']);self.assertIn('2 performances',r['reason'])
    def test_deduplicates_by_provider_and_item(self):
        row={'candidate_type':'recording','provider':'test','external_id':'alpha','artist_id':'grateful-dead',
             'title':'Same','observed_date':'1977-05-08','source_url':'https://archive.org/details/etree'}
        a.ingest(self.db,self.cat,row);a.ingest(self.db,self.cat,row)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM candidate').fetchone()[0],1)
    def test_rejects_unknown_artist_and_non_https(self):
        row={'candidate_type':'recording','provider':'test','external_id':'alpha','artist_id':'not-known',
             'title':'Test','observed_date':'1977-05-08','source_url':'https://archive.org/'}
        with self.assertRaises(ValueError):a.ingest(self.db,self.cat,row)
        row['artist_id']='grateful-dead';row['source_url']='javascript:alert(1)'
        with self.assertRaises(ValueError):a.ingest(self.db,self.cat,row)
    def test_bad_dates_are_not_matched(self):
        self.assertIsNone(a.a_date('1971-02-31'))
        self.assertIsNone(a.a_date('not a date'))
        self.assertEqual(a.a_date('1977.05.08'),'1977-05-08')
    def test_aliases_and_creator(self):
        ent=next(e for e in self.cat['entities'] if e['id']=='grateful-dead')
        self.assertTrue(a.resolve_from_creator(['Grateful Dead'],ent))
        self.assertFalse(a.resolve_from_creator(['Dead & Company'],ent))
    def test_duplicate_cannot_reset_review(self):
        row={'candidate_type':'event','provider':'test','external_id':'gamma','artist_id':'goose',
             'title':'Test show','observed_date':'2027-01-01','source_url':'https://ticketmaster.com/'}
        id=a.ingest(self.db,self.cat,row)
        self.db.execute("UPDATE candidate SET status='rejected' WHERE id=?",(id,));self.db.commit()
        a.ingest(self.db,self.cat,row)
        self.assertEqual(self.db.execute('SELECT status FROM candidate WHERE id=?',(id,)).fetchone()[0],'rejected')

if __name__=='__main__':unittest.main()
