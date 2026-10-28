"""Prevent pending, ambiguous, synthetic or tampered leads entering public catalog."""
import copy
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import approved_recordings as a
import research_agent as agent
from scripts import stage_approved as stage


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.cat = agent.catalog()
        self.shows = self.cat['historical_shows']
        self.seed = {r['id']:r for r in self.cat['recording_sources'] if not r['id'].startswith('agent-')}
        self.base = {
            'id':'agent-1234567890abcdefab', 'show_id':'gd-1977-05-08',
            'artist_id':'grateful-dead','title':'Test source','kind':'Audience recording',
            'source_url':'https://archive.org/details/exampleUniqueItem123',
            'provider':'Internet Archive','description':'A verified external page.',
            'access':'Rights determined by custodian.', 'reviewed_at':'2026-10-26',
            'review_note':'Manually inspected identifier, band, show date and source page.'
        }
    def doc(self, rows):
        return {'schema':'jam-archive-approved-recordings-v1','recordings':rows}
    def test_approved_link_has_show_context(self):
        rows = a.validate_recordings(self.doc([self.base]), self.shows, self.seed)
        self.assertEqual(rows[0]['show_id'],'gd-1977-05-08')
        self.assertIn('Manually inspected',rows[0]['description'])
        self.assertNotIn('review_note',rows[0])
    def test_rejects_duplicate_source_url_and_id(self):
        b=copy.deepcopy(self.base); b['id']='agent-aaaaaa012345abcdef'; b['title']='Duplicate title'
        with self.assertRaisesRegex(ValueError, 'duplicates a source'):
            a.validate_recordings(self.doc([self.base,b]),self.shows,self.seed)
        b['source_url']='https://archive.org/details/otherUnique'; b['id']=self.base['id']
        with self.assertRaisesRegex(ValueError,'duplicate ID'):
            a.validate_recordings(self.doc([self.base,b]),self.shows,self.seed)
    def test_approval_rejects_unknown_or_mismatched_show(self):
        b={**self.base,'show_id':'abb-1971-03-12-late'}
        with self.assertRaisesRegex(ValueError,'match'):
            a.validate_recordings(self.doc([b]),self.shows,self.seed)
    def test_review_note_and_date_required(self):
        for changed in ({'review_note':'Approved'}, {'reviewed_at':'2099-01-01'}):
            with self.assertRaises(ValueError):
                a.validate_recordings(self.doc([{**self.base,**changed}]),self.shows,self.seed)
    def test_https_only_and_no_credentials(self):
        for url in ['javascript:alert(1)','http://archive.org/details/id',
                    'https://me:password@archive.org/details/id',
                    'https://archive.org:9999/details/id']:
            with self.assertRaises(ValueError):
                a.validate_recordings(self.doc([{**self.base,'source_url':url}]),self.shows,self.seed)
    def test_pending_candidates_never_stage(self):
        with tempfile.TemporaryDirectory() as t:
            db=agent.connect(Path(t)/'temp.sqlite')
            try:
                candidate={'candidate_type':'recording','provider':'internet-archive',
                 'external_id':'exampleId','artist_id':'grateful-dead','title':'Example',
                 'observed_date':'1977-05-08','source_url':'https://archive.org/details/exampleId',
                 'creator_match':True}
                cid=agent.ingest(db,self.cat,candidate)
                with self.assertRaisesRegex(ValueError,'real, approved'):
                    stage.stage(cid,db)
            finally:db.close()
    def test_staging_rejects_mismatched_creator_and_accepts_reviewed_candidate(self):
        with tempfile.TemporaryDirectory() as t:
            db=agent.connect(Path(t)/'temp.sqlite')
            original=stage.APPROVED
            stage.APPROVED=Path(t)/'approved.json'
            stage.APPROVED.write_text(json.dumps(self.doc([])))
            try:
                candidate={'candidate_type':'recording','provider':'internet-archive',
                 'external_id':'unique123', 'artist_id':'grateful-dead',
                 'title':'Externally indexed item', 'observed_date':'1977-05-08',
                 'source_url':'https://archive.org/details/unique123','creator_match':False}
                cid=agent.ingest(db,self.cat,candidate)
                db.execute("UPDATE candidate SET status='approved',reviewed_at='2026-10-26',review_note='Verified exact performance date, lineup and original provider link.',proposed_show_id='gd-1977-05-08' WHERE id=?",(cid,))
                db.commit()
                with self.assertRaisesRegex(ValueError,'Creator match'):
                    stage.stage(cid,db)
                db.execute('UPDATE candidate SET evidence_json=? WHERE id=?',(json.dumps({'creator_match':True}),cid));db.commit()
                result=stage.stage(cid,db)
                self.assertEqual(result['show_id'],'gd-1977-05-08')
                self.assertEqual(len(json.loads(stage.APPROVED.read_text())['recordings']),1)
                with self.assertRaisesRegex(ValueError,'already staged'):
                    stage.stage(cid,db)
            finally:
                stage.APPROVED=original
                db.close()

if __name__=='__main__': unittest.main()
